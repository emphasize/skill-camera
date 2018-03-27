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
following class, ensure webcam is a priority skill!

    class VisionFeed(object):
        def __init__(self):
            self.m = None
            self.feed = None
            # default picture
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

        def shutdown(self):
            self.event_thread.join(0)

## Credits
JarbasAI