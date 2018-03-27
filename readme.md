## Camera skill
webcam for mycroft

## Description
take pictures with webcam, share image objects with other processes, send image file path in messagebus

you should make this a priority skill, it is meant to be used by other skills, it is needed because only 1 skill can access the webcam at a time

NOTE: this skill does not auto-reload, requires manual reboot

## Examples
* "take a picture"


## Using webcam in other skills

if you want to get a file path for the latest picture you can use the
messagebus to get a file path


    def initialize(self):
        self.add_event("webcam.picture", self.get_the_feed)
        self.emitter.emit(Message("webcam.request"))


    def get_the_feed(self, message):
        file_path = message.data.get("path")


you can also get the latest webcam frame as a numpy array by using the
CameraFeed class, ensure webcam is a priority skill!

    from share_camera import CameraFeed

    feed = CameraFeed()
    frame = feed.get().copy()

## email and privacy

there is an option to send taken pictures by mail in addition to storing them

your emails can be read by Mycroft Home, for privacy reasons this is not
used and you need to edit your configuration file

        ~/.mycroft/mycroft.conf

if it does not exist create it, this file must be valid json, add the
following to it

        "email": {
            "email": "send_from@gmail.com",
            "password": "SECRET",
            "destinatary": "send_to@gmail.com"
        }

email will now be sent from here, the destinatary is the same email if not
provided

skill settings were not used or your email and password would be stored in
mycroft home backend



## TODOS

- fix shutdown

## Credits
JarbasAI