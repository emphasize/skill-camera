## Camera skill
webcam for mycroft

## Description
take pictures with webcam, share image objects with other processes, send image file path in messagebus

you should make this a priority skill, it is meant to be used by other skills, it is needed because only 1 skill can access the webcam at a time

## Examples
* "take a picture"


## Using webcam in other skills

if you want to get a file path for the latest picture you can use the
messagebus to get a file path


    def initialize(self):
        self.emitter.emit(Message("webcam.request"))
        self.add_event("webcam.picture", self.get_the_feed)

    def get_the_feed(self, message):
        file_path = message.data.get("path")


you can also get the latest webcam frame as a numpy array by using the
CameraFeed class, ensure webcam is a priority skill!

    from share_camera import CameraFeed

    feed = CameraFeed()
    frame = feed.get().copy()

## Credits
JarbasAI