from mycroft.skills.core import intent_handler, intent_file_handler
from mycroft import MycroftSkill
from mycroft.util.log import LOG
from mycroft.util.audio_utils import play_wav, play_mp3
from os.path import join
import time
from os.path import dirname, exists, expanduser
from os import makedirs
import json

try:
    import cv2
    from imutils.video import VideoStream
    #from shared_camera import Camera
    import yagmail
except ImportError:
    # re-install yourself
    from msm import MycroftSkillsManager
    msm = MycroftSkillsManager()
    msm.install_by_url("https://github.com/emphasize/skill-camera", True)
    # trigger reload
    msm.reload_skill("skill-camera")


__author__ = 'jarbas'


class WebcamSkill(MycroftSkill):
    def __init__(self):
        self.create_settings_meta()
        super(WebcamSkill, self).__init__()
        platform = self.config_core.get("enclosure", {}) \
            .get("platform", "unknown")
        self.use_pi = platform.lower() in ["mycroft_mark_2", "mycroft_mark_1", "picroft", "unknown",
                                           "raspbian", "raspberry", "pi"]

        if "video_source" not in self.settings:
            self.settings["video_source"] = 0
        if "mail_picture" not in self.settings:
            self.settings["mail_picture"] = False
        if "play_sound" not in self.settings:
            self.settings["play_sound"] = True
        if "picture_path" not in self.settings:
            self.settings["picture_path"] = expanduser("~/webcam")
        if "camera_sound_path" not in self.settings:
            self.settings["camera_sound_path"] = join(dirname(__file__),
                                                      "camera.wav")

        if not exists(self.settings["picture_path"]):
            makedirs(self.settings["picture_path"])

        # private email
        if yagmail is not None:
            mail_config = self.config_core.get("email", {})
            self.email = mail_config.get("email")
            self.password = mail_config.get("password")
            self.target_mail = mail_config.get("destinatary", self.email)

        self.camera = None
        self.last_timestamp = 0

    def initialize(self):
        LOG.info("initializing videostream")

        def notify(text):
            self.emitter.emit(Message(text))

        self.camera = Camera(
            VideoStream(src=self.settings["video_source"],
                        usePiCamera=self.use_pi), callback=notify)
        self.last_timestamp = time.time()

    def get_intro_message(self):
        self.speak_dialog("priority")

    def mail_picture(self, picture):
        if self.settings["mail_picture"]:
            title = "Mycroft Camera Skill"
            body = ""
            # try private sending
            if yagmail is not None and self.email and self.password:
                with yagmail.SMTP(self.email, self.password) as yag:
                    yag.send(self.target_email, title, [body, picture])
            else:
                self.speak_dialog("send.fail")
                return False
            self.speak_dialog("send")
            return True
        return False

    @property
    def last_frame(self):
        self.last_timestamp = time.time()
        if self.camera:
            return self.camera.get().copy()
        return None

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
                        "name": "mail_picture",
                        "fields": [
                            {
                                "type": "label",
                                "label": "want to email taken pictures? check the repository for "
                                         "additional instructions"
                            },
                            {
                                "type": "checkbox",
                                "name": "mail_picture",
                                "label": "mail_picture",
                                "value": "false"
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

        pic_path = join(self.settings["picture_path"], time.asctime() +
                        ".jpg")
        cv2.imwrite(pic_path, self.last_frame)
        self.mail_picture(pic_path)
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
