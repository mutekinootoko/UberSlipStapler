# UberSlipStapler
This program is designed for processing receipts sent by Uber Taiwan, the text processing only works with Taiwanese language.
Uber Taiwan sends out two emails on every ride, which is required by Taiwanese law.
One is the main receipt and the other contains car rental informations.
This python program collects Uber receipts from Gmail acccount, parses infomations, and combines ("staples") the two matching emails (of each ride) into one pdf file. Great for applying travel reimbursements. 

基於台灣相關法令，
台灣 Uber 在每趟租車服務後，都會寄出兩份 email 收據，一封主要收據，另外一封是租車資訊。
這 python 程式可將 Gmail 帳號內的收據讀取出來，取出租車資訊，並且將對應的兩封收據信合併存成一份 pdf 檔案。
非常適合公司報帳用。

## Usage

### Requirements
For macOS, 
```
brew install caskroom/cask/wkhtmltopdf
```
Other OS, see https://wkhtmltopdf.org/

Install dependencies
```
pip install -r requirement.txt
```

### Gmail OAuth2
To enable Gmail API:
1. Use [this wizard](https://console.developers.google.com/start/api?id=gmail) to create or select a project in the Google Developers Console and automatically turn on the API. Click Continue, then Go to credentials.
2. On the Add credentials to your project page, click the Cancel button.
3. At the top of the page, select the OAuth consent screen tab. Select an Email address, enter a Product name if not already set, and click the Save button.
4. Select the Credentials tab, click the Create credentials button and select OAuth client ID.
5. Select the application type Other, enter the name "Gmail API Quickstart", and click the Create button.
6. Click OK to dismiss the resulting dialog.
7. Click the download icon (Download JSON) button to the right of the client ID.
8. Move this file to your working directory and rename it client_secret.json.

or Read *Step 1* in https://developers.google.com/gmail/api/quickstart/python

### GMAIL_USER_ID or `settings.py`
Fill this variable at `uberSlipStapler.py` file
```
GMAIL_USER_ID = None
```
with your own gmail address.

OR

Create `settings.py` file, with `GMAIL_USER_ID = <your gmail address>`.

### Run
```
python uberSlipStapler.py
```
First time running this program will ask you to login with google account, 
```
Search for uber slip in 2018/6
/Library/Python/2.7/site-packages/oauth2client/_helpers.py:255: UserWarning: Cannot access credentials.json: No such file or directory
  warnings.warn(_MISSING_FILE_MESSAGE.format(filename))

Go to the following link in your browser:

    https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly&redirect_ur........

Enter verification code:
```
follow the instructions (you might have to re-run the program after this). 
Make sure you have `client_secret.json` file. (see Gmail OAuth2 section)

For more options:
```
python uberSlipStapler.py -h
```

## Program Details

### Main receipt message and Rental slip

### Gmail search query

### Text processing