import cv2.cv as cv
import pytesseract
gray = cv.LoadImage('GetCaptcha.gif', cv.CV_LOAD_IMAGE_GRAYSCALE)
cv.Threshold(gray, gray, 231, 255, cv.CV_THRESH_BINARY)
api = pytesseract.TessBaseAPI()
api.Init(".", "eng", pytesseract.OEM_DEFAULT)
api.SetVariable(
    "tessedit_char_whitelist", "0123456789abcdefghijklmnopqrstuvwxyz")
api.SetPageSegMode(pytesseract.PSM_SINGLE_WORD)
pytesseract.SetCvImage(gray, api)
print api.GetUTF8Text()
