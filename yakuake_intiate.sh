#!/bin/bash
#qdbus org.kde.yakuake /yakuake/sessions addSessionQuad


INITIAL_ID=`qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.activeSessionId`
function addSession {
	SESSION_ID=$(qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.addSession)
	qdbus org.kde.yakuake /yakuake/tabs setTabTitle $SESSION_ID "$1"
	if [ ! -z "$2" ]; then
		echo $2
		qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.runCommandInTerminal $SESSION_ID "$2"
    	fi
}

number_of_tabs=$(echo $1 | grep "^-\?[0-9]*$")

if [ !-z $number_of_tabs] 2>/dev/null;
	then
		echo "Please provide the number of tabs to be opened with canworks enviroment"
		exit
	else
		for NUMBER in $(seq 1 $number_of_tabs)
		do
			echo $NUMBER
			#addSession "Canworks "$NUMBER "cd /home/kaali/Programs/Python/Canworks/ && source bin/activate && cd Canworks"
			#addSession "Canworks "$NUMBER "top"
			addSession "Top" "top"
		done
		echo "Success!!"
fi


#qdbus org.kde.yakuake /yakuake/sessions org.kde.yakuake.removeSession $INITIAL_ID
