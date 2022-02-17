Diffhest
===
A simple webhook for Phabricator. Should be triggered for each new Differential Revision created. If a revision title starts with a Maniphest Task number, like `T1337: fix stuff`, it will automagically link the revision to a corresponding Task.

## How to
Create a Herald Webhook in your phabricator, point it to your IP and run the webservice:
```
python3 -m venv venv
. venv/bin/activate
python3 -m pip install -r requirements.txt -e .
python3 -m diffhest \
  --phabricator https://my.phabricator.org \
  --phabricator_token api-userCONDUITtoken \
  --phabricator_hmac PhabricatorWebHookHMAC \
  --port 8080
```
Or even better create `.env` file with corresponding variables and use docker:
```
# .env:
DIFFHEST_PHABRICATOR_URL=...
DIFFHEST_PHABRICATOR_TOKEN=...
DIFFHEST_PHABRICATOR_HMAC=...
DIFFHEST_PORT=...

# run
docker-compose up --build
```
