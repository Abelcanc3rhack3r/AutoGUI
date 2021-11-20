# AutoGUI

Problem Statement:

Many administrative tasks that people carry out using
the Windows GUI usually involves some sort of standard operating procedure (SOP).
The hypothesis that this program is built on that SOP can be represented as an algorithm 
given some initial parameters ,and the information available to the user on the GUI
(in the form of filenames, text blocks ) completely determines
the series of steps to be executed in the SOP.


Currently, macros are available for many apps. Windows power automate hosts automation interfaces for many windows apps.
However, a universal AutoGUI interface which allows cross-app automation for all possible apps with a UI has not been well documented. 

This program aims to replicate as many manual procedures done with the windows/ any platform GUI as possible.
This may include: browser GUI automation, App GUI automation, command line automation etc etc. The app is designed to interact indirectly with the output 
from the screen as well as elements on the screen (in the form of screenshots) , and not via API to any application interface. Thus, the app strives to be platform and
App agnostic.


For example, say an admin has an excel sheet of the 
products she needs to buy from suppliers. Under
the suppliers column, if the supplier name is NTUC fairprice,
then the next step would be to visit the NTUC fairprice website to
make a purchase, and if the supplier name is Watsons, then
she must appropriately visit the Watsons website.

Administrati

What this App Aims to Do:

The AutoGUI app aims to decipher what is the sequence of steps 
required and what content to fill in for each form from recording down
each user input (i.e button clicks and keystrokes) , for different variations
Of the same task( for instance, visiting different supplier website), as well as by recording
down what was on the screen (which the user can use as input to the SOP algorithm).

By using machine learning , it aims to capture which inputs are similar between 
