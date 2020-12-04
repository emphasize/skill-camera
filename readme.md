## Camera skill
[![Donate with Bitcoin](https://en.cryptobadges.io/badge/micro/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)](https://en.cryptobadges.io/donate/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/jarbasai)
<span class="badge-patreon"><a href="https://www.patreon.com/jarbasAI" title="Donate to this project using Patreon"><img src="https://img.shields.io/badge/patreon-donate-yellow.svg" alt="Patreon donate button" /></a></span>
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/JarbasAl)

webcam for mycroft

## Description
take pictures with webcam, share image objects with other processes, send image file path in messagebus

you should make this a priority skill, it is meant to be used by other skills


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
Camera class, ensure webcam is a priority skill!

    from shared_camera import Camera

    c = Camera()
    frame = c.get()

## privacy

# email

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

# Using multiple Sources

*Draft*

*Note*: You have to tick the checkbox in home.mycroft.ai' skill settings
        under video_sources ("Use multiple sources")

By default the skill is handling one source that is connected to the device.
To be able to stream multiple remote streams you have to edit the user conf
like above and add your stream(s) like this example

        "cams": {
            "door": "http://...",
            "garden": "http://...",
            "...": "..."
        }

The "key" is part of the intent to call those specific stream
eg "show cam door"

## Credits
JarbasAI
