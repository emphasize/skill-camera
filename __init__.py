from mycroft.skills.core import MycroftSkill, intent_file_handler
from mycroft.util.log import LOG
from mycroft.util import play_wav, play_mp3
from multiprocessing.managers import BaseManager
from queue import LifoQueue
from os.path import join
from imutils.video import FPS
from imutils.video import VideoStream
import time
import cv2
from os.path import dirname, exists, expanduser
from os import makedirs
from threading import Thread


class VisionFeed(object):
    def __init__(self):
        self.m = None
        self.feed = None
        self.stock = cv2.imread(join(dirname(__file__), "no_feed.jpg"))
        self.current_frame = self.stock
        self.event_thread = Thread(target=self.connect)
        self.event_thread.setDaemon(True)
        self.event_thread.start()

    def connect(self):
        LOG.info("Connecting to webcam skill")
        flag = False
        feed_queue = LifoQueue(1)
        BaseManager.register('get_feed', callable=lambda: feed_queue)

        while not flag:
            try:
                self.m = BaseManager(address=('127.0.0.1', 56600),
                                     authkey=b'abc')
                self.m.connect()
                self.feed = self.m.get_feed()
                flag = True
                LOG.info("Connected to webcam skill")
            except:
                self.m = None
                self.feed = None
                LOG.error("webcam skill is not running")
                time.sleep(5)

    def get(self):
        try:
            self.current_frame = self.feed.get_nowait()
        except Exception as e:
            if self.current_frame is None:
                return self.stock
        return self.current_frame

    def get_path(self, path=None):
        try:
            self.current_frame = self.feed.get_nowait()
        except Exception as e:
            LOG.warning(e)
        if path is None:
            path = dirname(__file__) + "temp.jpg"
        if self.current_frame is not None:
            cv2.imwrite(path, self.current_frame)
            return path
        return None

    def set(self, frame=None):
        if frame is not None:
            try:
                self.feed.put_nowait(frame)
            except:
                self.get()


class SharedVisionFeed(object):
    def __init__(self):
        feed_queue = LifoQueue(1)
        BaseManager.register('get_feed', callable=lambda: feed_queue)
        try:
            self.m = BaseManager(address=('', 56600),
                             authkey=b'abc')
            self.server = self.m.get_server()
            self.t = Thread(target=self.start)
            self.t.setDaemon(True)
            self.t.start()
        except Exception as e:
            LOG.warning("Could not start broadcasting vision, please stop "
                        "all "
                      "clients trying to read from 56600 and re-start")
            LOG.error(e)

    def start(self):
        self.server.serve_forever()

    def shutdown(self):
        self.t.join(0)
        self.t = None


__author__ = 'jarbas'


class WebcamSkill(MycroftSkill):

    def __init__(self):
        super(WebcamSkill, self).__init__()
        platform = self.config_core.get("enclosure", {}) \
            .get("platform", "unknown")
        self.use_pi = platform.lower() in ["picroft", "mark_1", "mark1",
                                           "raspbian", "raspberry", "pi"]

        if "video_source" not in self.settings:
            self.settings["video_source"] = 0
        if "picture_path" not in self.settings:
            self.settings["picture_path"] = expanduser("~/webcam")
        if "camera_sound_path" not in self.settings:
            self.settings["camera_sound_path"] = join(dirname(__file__),
                                                      "camera.wav")

        if not exists(self.settings["picture_path"]):
            makedirs(self.settings["picture_path"])

        self.feed = cv2.imread(join(dirname(__file__), "no_feed.jpg"))
        self.vision_thread = None

        LOG.info("initializing videostream")
        self.vs = VideoStream(src=self.settings["video_source"],
                              usePiCamera=self.use_pi).start()
        self.log.info("Warming up camera")
        time.sleep(3)
        self.fps = None

        LOG.info("Starting shared vision feed")
        self.vision_server = SharedVisionFeed()
        self.shared_vision = VisionFeed()
        self.last_timestamp = time.time()

    def initialize(self):
        self.vision_thread = Thread(target=self.read_frame)
        self.vision_thread.setDaemon(True)
        self.vision_thread.start()
        self.add_event("webcam.request", self.handle_get_picture)

    def read_frame(self):
        self.feed = self.vs.read()
        if self.feed is not None:
            self.last_timestamp = time.time()
            self.shared_vision.set(self.feed.copy())

    @intent_file_handler("take_picture.intent")
    def handle_take_picture(self, message):
        if self.settings["camera_sound_path"]:
            if ".wav" in self.settings["camera_sound_path"]:
                play_wav(self.settings["camera_sound_path"])
            elif ".mp3" in self.settings["camera_sound_path"]:
                play_mp3(self.settings["camera_sound_path"])

        cv2.imwrite(join(self.settings["picture_path"], time.asctime() +
                    ".jpg"), self.feed)

    def handle_get_picture(self, message):
        if self.feed is not None:
            path = join(self.settings["picture_path"], time.asctime() + ".jpg")
            cv2.imwrite(path, self.feed)
            self.emitter.emit(message.reply("webcam.picture", {"path": path}))

    def shutdown(self):
        self.vs.stop()
        if self.vision_thread:
            self.vision_thread.join(10)
        self.vision_thread = None
        self.shared_vision.shutdown()
        super(WebcamSkill, self).shutdown()


def create_skill():
    return WebcamSkill()
