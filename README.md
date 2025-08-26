# Obsidian properties and tasks loader

## Purpose:
Is to create python based programm which works with obsidian daily notes, extracts data from them and loads data to storage where this data could be used.
Also includes configurable reward system which gives you rewards from completing habits and tasks

## Daily note structure
### Habits
Habits are **properties**. They must be the same throughout whole obsidian DailyNotes, else it dupes different habits, like 'Sport', 'sport', 'sport ' and etc. It's recommended to create Daily note tamplate which automatically will be the same for all your Daily Notes.
Also habits need to have *Day begin* and *Day end*. It's special kind of habits which is processed in special way.
There's csv file in **data** folder, which contains habits and rewards for completing them. 
>Note
>rewards are recieved if habit reaches targer. It could be also negative reward, like "spending time in phone". While habits are filled manually.
## Tasks
Tasks must be list of checkboxes, with name of tasks and reward in brackets.
All marked tasks will be completed and reward will be recieved
## Day begin and day end.
It's special kind of habit is calculated in special way so it's not in list of all habits and stored in _sleep\_rewards.csv_# Obsidian 