# HnG-Server-Picker
ℹ️**Information**

The H&G Server Picker application lets you pick which server(s) you would like to play on, and no matter how long you spend in queue, you will only find matches on those servers.

If you are from a smaller region such as Oceania, South America or Asia you could block your home server(s) to skip the initial time it takes for the matchmaker to start searching in other regions, which could be useful if not many players in your region are online and you wanted fast consecutive matches on the next best server.

You can queue into your friends matches, or be a squad member with it on and load in successfully without any issues. 

IMPORTANT: The developers are constantly adding and removing servers that have different IP's. If you find that you are popping into matches with high ping, it's probably because they added a new server. If you open your H&G Sync tab and scroll down to where you see /M, you can look along that line until you see "actionhost= (IP HERE)". Copy this IP, and in the app click "Add Server". Give it a name, paste the IP, and assign a flag. 

If you don't want to add each server manually this way, I will be updating the "Releases" tab with new versions of the app when they add new servers. So you can just come to this page and download it again. I tried coding an updater that would allow me to push updates using github, but couldn't get it to work. I'll try to implement this feature in future releases.  


<img width="544" height="549" alt="Screenshot_1" src="https://github.com/user-attachments/assets/406057f7-30aa-45d8-a598-e3433e973c70" />


The app is available in English, Chinese, German, Korean, Portuguese, Spanish, Russian, Thai and Vietnamese. 

⬇️ **Download**

[Download here](https://github.com/TrickshotOCE/HnG-Server-Picker/releases)

After downloading the app you will be prompted with a "Windows protected your PC" message. This happens because the app isn't digitally signed (code-signing certificates cost money) and hasn't been downloaded enough times yet for Microsoft to recognize it as "trusted."

For the app to work:

Click More info on the warning screen -> Click Run anyway.
<img width="785" height="362" alt="Screenshot_5" src="https://github.com/user-attachments/assets/da503ed8-72fe-44ac-aeb0-a47af6f0b047" />

The source code is fully available in this repo if you'd like to review it yourself.

😀**Checking it works**
I recommend clicking "Block All"


Creating or deleting Windows Firewall rules requires admin privileges — this is a Windows restriction, not something the app chooses. When you launch it, Windows will show a UAC prompt ("Do you want to allow this app to make changes to your device?"); you need to accept it for the app to work at all. If you decline, the app will close, since it can't do anything useful without firewall access.










❔FAQ
1. How does it work?

   
   ⚪ How does it work?   
   ⚪ How does it work?
   ⚪ How does it work?
   ⚪ How does it work?


   
matchmaking just puts you wherever it wants. This app works around that by blocking or unblocking each server's IP address in Windows Defender Firewall, so the game's matchmaker can only "see" the servers you've chosen to leave open.
