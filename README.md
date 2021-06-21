Discord Donation Bot 
=================

This is a chatbot that enables donations on discord via Cashapp or Venmo. 

### Features

- Ability to accept payments from Cashapp or Venmo.  
- Fully automatic chatbot. 

Commands: 
```
.donate
This command is used to start the donation process for a user. 
.setprice <price>
This command is used to set/change price of donation. 
.setrole <@role>
This command is used to  set/change role of donation. 
.setpayment <cashapp/venmo> <address>
This command is used to  set/change address of payment method.
```

# How does it work?
Once the user sends payment including a unique identifying note, the bot then checks email to verify if the note and payment amount matches and then it grants a role to the user. 

<img src="/screenshot/example.gif?raw=true">
