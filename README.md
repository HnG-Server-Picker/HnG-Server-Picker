# HnG-Server-Picker
ℹ️**Information**

H&G Server Picker lets you decide which server(s) you would like to play on, and no matter how long you spend in queue, you will only find matches on those servers.

IMPORTANT: The developers are constantly adding and removing servers that have different IP's. If you find that you are popping into matches with high ping, it's probably because they added a new server. If you open your H&G Sync tab and scroll down to where you see /M, you can look along that line until you see "actionhost = (IP HERE)". Copy this IP, and in the app click "Add Server". Give it a name, paste the IP and assign a flag. 

If you don't want to add each server manually this way, I will be updating the "Releases" tab with new versions when they add new servers. So you can just come to this page and download it again. 


<img width="541" height="596" alt="Screenshot_11" src="https://github.com/user-attachments/assets/f7215efb-5a80-40b3-8166-89e02a9471fc" />


The app is available in English, Chinese, German, Korean, Portuguese, Spanish, Russian, Thai and Vietnamese. 

⬇️ **Download** 

[Download here](https://github.com/HnG-Server-Picker/HnG-Server-Picker/releases) - Click the .exe file.

After downloading the app you will be prompted with a "Windows protected your PC" message. This happens because the app isn't digitally signed (code-signing certificates cost money).

For the app to work:

Click More info on the warning screen -> Click Run anyway.
<img width="785" height="362" alt="Screenshot_5" src="https://github.com/user-attachments/assets/da503ed8-72fe-44ac-aeb0-a47af6f0b047" />

The app uses the windows firewall to block the IP's. Creating or deleting Windows Firewall rules requires admin privileges — this is a Windows restriction. When you launch it, Windows will show a UAC prompt ("Do you want to allow this app to make changes to your device?"); you need to accept it for the app to work at all. If you decline, the app won't open.


✅**Checking it works**

I recommend clicking "Block All" on the app and opening H&G. Open your H&G sync and look for ping:(IP). They should all say :Timeout as shown in the screenshot below. If you see any IP's that say "OK" at the end, they are not blocked. You can add the IP manually yourself, or wait for an update. 

<img width="188" height="135" alt="Screenshot_7" src="https://github.com/user-attachments/assets/82f43cab-1417-43ee-bde8-c24b1be7f669" />

You can also search for Windows Defender Firewall and go to "Outbound Rules" where you should see a rule named "ServerPicker_Block". If you double click on this and go to "Scope", you will see all of the blocked IP's. 

<img width="681" height="213" alt="Screenshot_8" src="https://github.com/user-attachments/assets/522c1859-b1d1-449f-8d61-f052a629e225" />


❔**FAQ**

1. Can I leave H&G open when blocking or unblocking servers?
   
   It is highly recommended to restart H&G every time you make any changes.

2. Can I join a friends match even if they are playing on a server I have blocked?

   Yes. Blocking the servers doesn't restrict you from joining a friends match, or being a squad member and joining a match.

3. Do I need to block / unblock servers every time I open the app?

   No. The app will remember your previously blocked severs, and selected language from when you last had it open.

4. What happens when I close the app?

   When closed, all firewall rules will be deleted instantly and all servers will be in an unblocked state. 

5. Is this cheating? Can I get banned for this?

   No this is not cheating, no game files are being changed. This application only blocks servers (IP's) using the windows firewall. I have not checked with the developers if this is allowed, so use at your own risk.

6. Why do some servers say "N/A" and not give a ping reading?

   I'm honestly not sure, but it's nothing on your end. The server itself simply can't be pinged so no reading can be shown. This happens for the Singapore and Australian servers, as well as one French and German server.

7. I keep seeing this "Unable to ping game servers" message. What is going on?

   Before searching for a match you need to let H&G sync actually ping the IP's that you have unblocked. When H&G opens just give it a minute before you start searching for a match and it should be fine.

   <img width="476" height="283" alt="Screenshot_10" src="https://github.com/user-attachments/assets/2c887822-838d-49f3-accc-1d70aa77a2aa" />


