Beta site currently disabled. Going to have to restore urls in the following places:

scenable/urls.py
- Put in a catch-all above all normal links. Remove it and uncomment and commented-out ones.
scenable/accounts/urls.py
- Put in a catch-all for everything but password reseting (to still allow biz admin users to reset passwords).
templates/orgadmin/*_item.html
- Removed View on site links