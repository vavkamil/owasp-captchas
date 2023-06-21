from burp import IBurpExtender
from burp import IIntruderPayloadGeneratorFactory
from burp import IIntruderPayloadGenerator
from java.net import URL, HttpURLConnection
from java.io import DataOutputStream
from java.io import BufferedReader, InputStreamReader
import json
import time

class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):

    def registerExtenderCallbacks(self, callbacks):
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("gRecaptcha payload generator")
        callbacks.registerIntruderPayloadGeneratorFactory(self)

    def getGeneratorName(self):
        return "gRecaptcha payload generator"

    def createNewInstance(self, attack):
        return IntruderPayloadGenerator()

class IntruderPayloadGenerator(IIntruderPayloadGenerator):

    def hasMorePayloads(self):
        # Always generate a new payload for each request
        return True

    def getNextPayload(self, baseValue):
        # Generate a new gRecaptchaResponse for each request
        payload = self.get_gRecaptchaResponse()
        return payload

    def reset(self):
        pass

    def get_gRecaptchaResponse(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        url_create_task = 'https://api.anti-captcha.com/createTask'
        data_create_task = {
            "clientKey":"ANTI-CAPTCHA-API-KEY",
            "task":
                {
                    "type":"RecaptchaV2TaskProxyless",
                    "websiteURL":"https://xss.vavkamil.cz/captcha.php",
                    "websiteKey":"6Lf3s6smAAAAAJhW3or_xM30ZriJpD2zAHAKr2JY"
                },
            "softId": 0
        }
        response = self.make_post_request(url_create_task, headers, data_create_task)
        task_id = json.loads(response)['taskId']

        time.sleep(5)  # Wait for the task to complete

        url_get_result = 'https://api.anti-captcha.com/getTaskResult'
        while True:
            data_get_result = {
                "clientKey":"ANTI-CAPTCHA-API-KEY",
                "taskId":task_id
            }
            result = self.make_post_request(url_get_result, headers, data_get_result)
            result_json = json.loads(result)
            if result_json['status'] == 'ready':
                gRecaptchaResponse = result_json['solution']['gRecaptchaResponse']
                return bytearray(gRecaptchaResponse, "utf-8")
            else:
                time.sleep(3)  # Wait before retrying

    def make_post_request(self, url_str, headers, data):
        url = URL(url_str)
        connection = url.openConnection()
        connection.setRequestMethod("POST")
        for key, value in headers.items():
            connection.setRequestProperty(key, value)

        connection.setDoOutput(True)
        connection.setDoInput(True)

        # Write the POST data
        data_output_stream = DataOutputStream(connection.getOutputStream())
        data_output_stream.writeBytes(json.dumps(data))
        data_output_stream.flush()
        data_output_stream.close()

        # Read the response
        input_stream = BufferedReader(InputStreamReader(connection.getInputStream()))
        response = []
        line = input_stream.readLine()
        while line is not None:
            response.append(line)
            line = input_stream.readLine()
        input_stream.close()
        return '\n'.join(response)

