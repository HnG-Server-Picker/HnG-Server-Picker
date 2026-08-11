# HnG-Server-Picker
ℹ️**Information**

The H&G Server Picker app lets you decide which server(s) you would like to play on, and no matter how long you spend in queue, you will only find matches on those servers.

If you are from a smaller region such as Oceania, South America or Asia you could block your home server(s) to skip the initial time it takes for the matchmaker to start searching in other regions, which could be useful if not many players in your region are online and you wanted fast consecutive matches on the next best server.

You can queue into your friends matches, or be a squad member with it on and load in successfully without any issues. 

IMPORTANT: The developers are constantly adding and removing servers that have different IP's. If you find that you are popping into matches with high ping, it's probably because they added a new server. If you open your H&G Sync tab and scroll down to where you see /M, you can look along that line until you see "actionhost= (IP HERE)". Copy this IP, and in the app click "Add Server". Give it a name, paste the IP, and assign a flag. 

If you don't want to add each server manually this way, I will be updating the "Releases" tab with new versions of the app when they add new servers. So you can just come to this page and download it again. 


<img width="544" height="549" alt="Screenshot_1" src="https://github.com/user-attachments/assets/406057f7-30aa-45d8-a598-e3433e973c70" />


The app is available in English, Chinese, German, Korean, Portuguese, Spanish, Russian, Thai and Vietnamese. 

⬇️ **Download**

[Download here](https://github.com/HnG-Server-Picker/HnG-Server-Picker/releases)

After downloading the app you will be prompted with a "Windows protected your PC" message. This happens because the app isn't digitally signed (code-signing certificates cost money) and hasn't been downloaded enough times yet for Microsoft to recognize it as "trusted."

For the app to work:

Click More info on the warning screen -> Click Run anyway.
<img width="785" height="362" alt="Screenshot_5" src="https://github.com/user-attachments/assets/da503ed8-72fe-44ac-aeb0-a47af6f0b047" />

The app uses the windows firewall to block the IP's. Creating or deleting Windows Firewall rules requires admin privileges — this is a Windows restriction, not something the app chooses. When you launch it, Windows will show a UAC prompt ("Do you want to allow this app to make changes to your device?"); you need to accept it for the app to work at all. If you decline, the app will close, since it can't do anything useful without firewall access.


✅**Checking it works**

I recommend clicking "Block All" on the app and opening H&G. Open your H&G sync and look for ping:(IP). They should all say :Timeout as shown in the screenshot below. If you see any IP's that say "OK" at the end, they are not blocked. You can add the IP manually yourself, or wait for an update. 

<img width="188" height="135" alt="Screenshot_7" src="https://github.com/user-attachments/assets/82f43cab-1417-43ee-bde8-c24b1be7f669" />



❔**FAQ**

1. Can i leave H&G open when blocking or unblocking servers?
   
   It is highly recommended to restart H&G every time you make any changes.

2. Can I join a friends match even if they are playing on a server I have blocked?

   Yes. Blocking the servers doesn't restrict you from joining a friends match, or being a squad member and joining a match.

3. Do I need to block / unblock servers every time I open the app?

   No. The app will remember your previously blocked severs, and selected language from when you last had it open.

4. What happens when I close the app?

   When closed, all firewall rules will be deleted instantly and all servers will be in an unblocked state. 

5. Is this cheating? Can I get banned for this?

   No this is not cheating, no game files are being changed. This application only blocks servers (IP's) using the windows firewall. I have not checked with the developers if this is allowed, so use at your own risk. 

❤️**Special Mention**

Big shoutout to Beng_ who made a guide in 2022 on blocking H&G IP's using the windows firewall. Without this, I wouldn't of been able to create this app, so big thanks to him. You can find his guide here: https://hngguide.dudwire.com/
