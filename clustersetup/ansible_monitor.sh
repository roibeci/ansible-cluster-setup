#!/bin/bash
#shell script to check ansible playbook

#count total number of tasks in playbook
TotalTaskNumber=$(cat ../ansible_playbook/tasks/main.yml | grep "\- name:" |grep -v "#"|wc -l)
#check last task running
LastTask=$(cat nohup.out | grep  "TASK" | tail -1|tr "\*" " ")
#total tasks comleted so far
var=$(cat nohup.out | grep  "TASK" | wc -l)
CompletedTasks=$(($var-4))
#find if there were failed tasks
isFinished=$(cat nohup.out | grep "PLAY RECAP")

if [ -z "$isFinished" ];
then
 echo "Playbook is still running -- Current status: "$CompletedTasks" / "$TotalTaskNumber" -- Task Name: "$LastTask" "
 exit 0
else
 echo "Ansible playbook has finished. Let's Check the status now !"
fi

isfailedTasks=$(cat nohup.out | tail -3 | grep -i failed  | awk '{print $6}')
patern="failed=0"
if [ "$isfailedTasks" = "$patern" ];
then
 echo "Ansible Completed Successfuly"
else
 #TNM=$(echo "$LastTask"|tr "\[" " "|tr "\]" " ")
 #TNM=$(echo "$LastTask"|tr "\[" "'[ " | tr "\]" "'] ")
 TNM=$(echo "$LastTask"|tr -d "[" | tr -d "]")
 TaskSearch=$(echo "$TNM" | awk '{$1="" ; print $0}' | awk '{$1=$1};1')
 echo "############" $TaskSearch
 Log=$(cat nohup.out | grep  "$TaskSearch" -A 1)
 echo "Error Found in "$TNM" "
 echo "Relevant Logs:"
 echo "$Log"
fi
