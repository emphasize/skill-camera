from mycroft.skills.core import MycroftSkill, intent_file_handler
from mycroft.util.log import LOG
from mycroft.util import play_wav, play_mp3
from shared_camera import SharedCamera, CameraFeed
from os.path import join
from imutils.video import VideoStream
import time
import cv2
from os.path import dirname, exists, expanduser
from os import makedirs
import json


__author__ = 'jarbas'


class WebcamSkill(MycroftSkill):
    def __init__(self):
        self.create_settings_meta()
        super(WebcamSkill, self).__init__()
        self.reload_skill = False
        platform = self.config_core.get("enclosure", {}) \
            .get("platform", "unknown")
        self.use_pi = platform.lower() in ["picroft", "mark_1", "mark1",
                                           "raspbian", "raspberry", "pi"]

        if "video_source" not in self.settings:
            self.settings["video_source"] = 0
        if "play_sound" not in self.settings:
            self.settings["play_sound"] = True
        if "picture_path" not in self.settings:
            self.settings["picture_path"] = expanduser("~/webcam")
        if "camera_sound_path" not in self.settings:
            self.settings["camera_sound_path"] = join(dirname(__file__),
                                                      "camera.wav")

        if not exists(self.settings["picture_path"]):
            makedirs(self.settings["picture_path"])

        LOG.info("initializing videostream")
        self.camera = SharedCamera(
            VideoStream(src=self.settings["video_source"],
                        usePiCamera=self.use_pi))
        self.feed = CameraFeed()
        self.last_timestamp = time.time()

    def get_intro_message(self):
        self.speak_dialog("priority")

    @property
    def last_frame(self):
        return self.feed.get().copy()

    def create_settings_meta(self):
        meta = {
            "name": "Camera Skill",
            "skillMetadata": {
                "sections": [
                    {
                        "name": "video_source",
                        "fields": [
                            {
                                "type": "label",
                                "label": "video source for webcam, usually 0"
                            },
                            {
                                "name": "video_source",
                                "type": "number",
                                "label": "video_source",
                                "placeholder": "0",
                                "value": "0"
                            }
                        ]
                    },
                    {
                        "name": "camera_sound_path",
                        "fields": [
                            {
                                "type": "label",
                                "label": "path to wav or mp3 sound file to play on picture taken"
                            },
                            {
                                "name": "camera_sound_path",
                                "type": "text",
                                "label": "camera_sound_path",
                                "placeholder": join(dirname(__file__),
                                                      "camera.wav"),
                                "value": join(dirname(__file__),
                                                      "camera.wav")
                            },
                            {
                                "type": "checkbox",
                                "name": "play_sound",
                                "label": "play sound on taking picture",
                                "value": "true"
                            }
                        ]
                    },
                    {
                        "name": "picture_path",
                        "fields": [
                            {
                                "type": "label",
                                "label": "where to save taken pictures"
                            },
                            {
                                "name": "picture_path",
                                "type": "text",
                                "label": "picture_path",
                                "placeholder": expanduser("~/webcam"),
                                "value": expanduser("~/webcam")
                            }
                        ]
                    }
                ]
            }
        }
        meta_path = join(dirname(__file__), 'settingsmeta.json')
        if not exists(meta_path):
            with open(meta_path, 'w') as fp:
                json.dump(meta, fp)

    def initialize(self):
        self.add_event("webcam.request", self.handle_get_picture)

    @intent_file_handler("take_picture.intent")
    def handle_take_picture(self, message):
        if exists(self.settings["camera_sound_path"]) and \
                self.settings["play_sound"]:
            if ".wav" in self.settings["camera_sound_path"]:
                play_wav(self.settings["camera_sound_path"])
            elif ".mp3" in self.settings["camera_sound_path"]:
                play_mp3(self.settings["camera_sound_path"])

        cv2.imwrite(join(self.settings["picture_path"], time.asctime() +
                         ".jpg"), self.last_frame)
        self.speak_dialog("picture")

    def handle_get_picture(self, message):
        path = join(self.settings["picture_path"],
                    time.asctime() + ".jpg")
        cv2.imwrite(path, self.last_frame)
        self.emitter.emit(message.reply("webcam.picture", {"path": path}))

    def shutdown(self):
        self.camera.stop_stream()
        self.camera.shutdown()
        super(WebcamSkill, self).shutdown()


def create_skill():
    return WebcamSkill()
