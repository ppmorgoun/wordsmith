#Free_Google_ASR.py
import speech_recognition as sr

class Free_Google_ASR:

    def __init__(self):
        self.recognizer = sr.Recognizer()
        # adjust for ambient noise
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 400
        
        self.microphone = sr.Microphone()
        # check that recognizer and microphone arguments are appropriate type
        if not isinstance(self.recognizer, sr.Recognizer):
            raise TypeError("`recognizer` must be `Recognizer` instance")

        if not isinstance(self.microphone, sr.Microphone):
            raise TypeError("`microphone` must be `Microphone` instance")


        # set up the response object
        self.response = {
            "success": True,
            "error": None,
            "transcription": None
        }

    """     with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("ready!") """

    def adjust_for_ambient_noise(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            

    def get_command(self):

        # adjust the recognizer sensitivity to ambient noise and record audio
        # from the microphone

        with self.microphone as source:
            print("started listening")
            self.audio = self.recognizer.listen(source, timeout=5)
            print("got something")

        # try recognizing the speech in the recording
        # if a RequestError or UnknownValueError exception is caught,
        #     update the response object accordingly
        try:
            self.response["transcription"] = self.recognizer.recognize_google(self.audio)
        except sr.RequestError:
            # API was unreachable or unresponsive
            self.response["success"] = False
            self.response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            self.response["error"] = "Unable to recognize speech"

        return self.response

    def test_loop(self):
        while(True):
            i = 0
            while(True):
                guess = self.get_command()
                if guess["transcription"]:
                    break
                if not guess["success"]:
                    break
                print(i, ": I didn't catch that. What did you say?\n")
                i+=1
                # if there was an error, stop the game
            if guess["error"]:
                print("ERROR: {}".format(guess["error"]))
                break
            # show the user the transcription
            print("You said: {}".format(guess["transcription"]))
