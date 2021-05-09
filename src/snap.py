import os, json, sqlite3, sys
from colorama import Fore, Style, Back
from datetime import datetime

class SetupSnap:
    def __init__(self):
        self.display_name = ""
        self.logged_in = False
        self.user_info = {}
        self.current_username = ""
        self.index = 0
        if os.path.isfile('user_info.json'):
            self.all_user_info = json.loads(open('user_info.json', 'r').read())
        else:
            self.all_user_info = {'UserInfo': []}
        self.db = sqlite3.connect('offbrandsnap.db')
        self.cursor = self.db.cursor()
        self.db.execute('''
CREATE TABLE IF NOT EXISTS UserInfo (
    username string,
    password string,
    logged_in INTEGER
);''')
        self.db.commit()

    def login(self, username, password):
        for i in range(len(self.all_user_info['UserInfo'])):
            if self.all_user_info['UserInfo'][i]['Username'] == username or self.all_user_info['UserInfo'][i]['Account Info']['DispName'] == username:
                username = self.all_user_info['UserInfo'][i]['Username']  # reset the value so we can continue on without errors
                self.cursor.execute(
                    f'SELECT logged_in FROM UserInfo WHERE username = "{username}"'
                )
                LI = self.cursor.fetchall()
                if LI[0][0] == 0:
                    print(
                        '[ERR]: You are attempting to log into an account that is already active.'
                    )
                    sys.exit(1)

                self.cursor.execute(
                    f'SELECT password FROM UserInfo WHERE username = "{username}"'
                )
                PASSWORD = self.cursor.fetchall()

                if password == PASSWORD[0][0]:
                    self.display_name = self.all_user_info['UserInfo'][i]['Account Info']['DispName']
                    self.user_info = self.all_user_info['UserInfo'][i]
                    break
                else:
                    print('[ERR]: Password Incorrect.')
                    sys.exit(1)
            if i == len(self.all_user_info['UserInfo']) - 1:
                print('[ERR]: Username is incorrect.')
                sys.exit(1)

        self.cursor.execute('INSERT INTO UserInfo(logged_in) VALUES(0)')
        self.logged_in = True
        self._set_index_()
    
    def _set_index_(self):
        for i in range(len(self.all_user_info['UserInfo'])):
            if self.all_user_info['UserInfo'][i]['Username'] == self.user_info['Username']:
                self.index = i

    def create_user(self, username, password):
        create = False
        if not self.all_user_info['UserInfo'] == []:
            for i in range(len(self.all_user_info['UserInfo'])):
                if username == self.all_user_info['UserInfo'][i]['Username']:
                    self.login(username, password)
                    break
                if i == len(self.all_user_info['UserInfo']) - 1:
                    create = True
        else:
            create = True

        if create == True:
            self.user_info.update({
                'Username': username,
                'Created': f'{datetime.now().strftime("%m/%d/%Y %H:%M:%S")}',
                'Account Info': {}
            })
            self.current_username = self.user_info['Username']
            self.all_user_info['UserInfo'].append(self.user_info)
            self.index = len(self.all_user_info['UserInfo']) - 1

            self.cursor.execute(f'''
    INSERT INTO UserInfo(username, password, logged_in) VALUES("{username}", "{password}", 0)'''
                                )
            self.db.commit()

            with open('user_info.json', 'w') as file:
                file.write(
                    json.dumps(self.all_user_info, indent=2, sort_keys=False))
                file.close()

            self.logged_in = True
            self._set_index_()

    def update(self):
        with open('user_info.json', 'w') as file:
            file.write(
                json.dumps(self.all_user_info, indent=2, sort_keys=False))
            file.flush()
            file.close()

    def create_display_name(self):
        if not 'DispName' in self.all_user_info['UserInfo'][
                self.index]['Account Info']:
            self.display_name = input(
                f'Display name for {self.current_username}: ')

            self.user_info['Account Info'].update(
                {'DispName': self.display_name})

            self.all_user_info['UserInfo'][self.index].update(self.user_info)

            self.update()

    def login_info(self):
        return (self.logged_in, self.all_user_info, self.user_info, self.index, self.db)


class SnapUi:
    def __init__(self, _info):
        """ GET THE BASIC INFORMATION FOR THE APP """
        # Users Information
        self.logged_in = _info[0]
        self.all_user_info = _info[1]
        self.user_info = _info[2]
        self.index = _info[3]

        # Database
        self.db = _info[4]
        self.cursor = self.db.cursor()

        # Display Name
        self.display_name = self.user_info['Account Info']['DispName']

        # Add Score(for total messages, can't send snaps lol)
        # Add total friends the user has
        if not 'Score' in self.user_info['Account Info'] and not 'Friends' in self.user_info['Account Info']:
            self.user_info['Account Info'].update({'Score': 0, 'Friends': 0, 'Pending Adds': [], 'All Friends': []})
        self.user_score = self.user_info['Account Info']['Score']
        self.total_friends = self.user_info['Account Info']['Friends']

    """ ALL HELPER FUNCTIONS FOR THE __start__ FUNCTION. NONE WILL BE USED IN MAIN BUT THE __start__ FUNCTION. """

    def __profile__(self):
        """ PRINT THE USERS PROFILE """
        self.__adds__()
        print(f'''
\t\t\t\t{self.display_name}\n\t\t\t\t({self.user_info['Username']})\n\t\t\t---------------------\n\t\t\tScore:\t\t{self.user_info['Account Info']['Score']}\n\t\t\tFriends:\t{self.user_info['Account Info']['Friends']}\n\t\t\t---------------------\n\n\t\t\tJoined: {self.user_info['Created']}\n'''
              )

    def __add_user__(self, username):
        for i in range(len(self.all_user_info['UserInfo'])):
            if self.all_user_info['UserInfo'][i]['Username'] == username:
                if not 'Pending Adds' in self.all_user_info['UserInfo'][i]['Account Info']:
                    self.all_user_info['UserInfo'][i]['Account Info'].update({'Pending Adds':[]})

                if not self.user_info['Username'] in self.all_user_info['UserInfo'][i]['Account Info']['Pending Adds']:
                    if not self.user_info['Username'] in self.all_user_info['UserInfo'][i]['Account Info']['All Friends']: 
                        self.all_user_info['UserInfo'][i]['Account Info']['Pending Adds'].append(self.user_info['Username'])

                        print(f'Successfully sent request to {username}!\n')
                    else:
                        print(f'{self.all_user_info["UserInfo"][i]["Account Info"]["DispName"]}({username}) is already your friend!\n')
                else: print('Request already sent!')
                break
            if i == len(self.all_user_info['UserInfo']) - 1:
                print(f'[USR NOT FOUND] The user {username} was not found.\n')
    
    def __adds__(self):
        if 'Pending Adds' in self.user_info['Account Info'] and len(self.user_info['Account Info']['Pending Adds']) > 0:
            print("\nYou Got Pending Adds:\n\t")
            for i in range(len(self.user_info['Account Info']['Pending Adds'])):
                print('\t', i + 1, ' > ' + self.user_info['Account Info']['Pending Adds'][i])

                accept = int(input(f'Accept {self.user_info["Account Info"]["Pending Adds"][i]}?[0 yes, 1 no] > '))

                if accept == 0:
                    new_friend = self.user_info['Account Info']['Pending Adds'][i]
                    self.user_info['Account Info']['Pending Adds'].remove(self.user_info['Account Info']['Pending Adds'][i])
                    self.user_info['Account Info']['All Friends'].append(new_friend)
                    self.user_info['Account Info']['Friends'] += 1

                    for i in range(len(self.all_user_info['UserInfo'])):
                        if self.all_user_info['UserInfo'][i]['Username'] == new_friend:
                            self.all_user_info['UserInfo'][i]['Account Info']['All Friends'].append(self.user_info['Username'])
                            self.all_user_info['UserInfo'][i]['Account Info']['Friends'] += 1
                            break
    
    def _all_friends_(self):
        if not self.user_info['Account Info']['All Friends'] == []:
            print('\n\n---------- ALL FRIENDS ----------\n')
            for i in range(len(self.user_info['Account Info']['All Friends'])):
                for x in range(len(self.all_user_info['UserInfo'])):
                    if self.all_user_info['UserInfo'][x]['Username'] == self.user_info['Account Info']['All Friends'][i]:

                        print('\t', i + 1, ' > ', self.all_user_info['UserInfo'][x]['Account Info']['DispName'], f'({self.user_info["Account Info"]["All Friends"][i]})')
            print('\n----------------------------------')
    
    def _user_exists_(self, user):
        if not user == self.user_info['Username'] and not user == self.user_info['Account Info']['DispName']:
            for i in range(len(self.all_user_info['UserInfo'])):
                if self.all_user_info['UserInfo'][i]['Username'] == user or self.all_user_info['UserInfo'][i]['Account Info']['DispName'] == user:

                    if not 'Mutual friends' in self.all_user_info['UserInfo'][i]['Account Info']:
                        self.all_user_info['UserInfo'][i]['Account Info'].update({'Mutual friends':[]})
                    if not 'Mutual friends' in self.user_info['Account Info']:
                        self.user_info['Account Info'].update({'Mutual friends': []})

                    # come back to this later.
                    for x in range(len(self.all_user_info['UserInfo'][i]['Account Info']['All Friends'])):
                        if self.all_user_info['UserInfo'][i]['Account Info']['All Friends'][x] in self.user_info['Account Info']['All Friends']:
                            if len(self.all_user_info['UserInfo'][i]['Account Info']['Mutual friends']) == 0:
                                self.all_user_info['UserInfo'][i]['Account Info']['Mutual friends'].append({self.user_info['Username']: [self.all_user_info['UserInfo'][i]['Account Info']['All Friends'][x]]})

                                self.user_info['Account Info']['Mutual friends'].append({self.all_user_info['UserInfo'][i]['Username']: [self.all_user_info['UserInfo'][i]['Account Info']['All Friends'][x]]})
                            else:
                                for t in range(len(self.all_user_info['UserInfo'][i]['Account Info']['Mutual friends'])):
                                    if not self.all_user_info['UserInfo'][i]['Account Info']['All Friends'][x] in self.all_user_info['UserInfo'][i]['Account Info']['Mutual friends'][t][self.user_info['Username']]:
                                        self.all_user_info['UserInfo'][i]['Account Info']['Mutual friends'][t][self.user_info['Username']].append(self.all_user_info['UserInfo'][i]['Account Info']['All Friends'][x])
                                    if not self.all_user_info['UserInfo'][i]['Account Info']['All Friends'][x] in self.user_info['Account Info']['Mutual friends'][t][self.all_user_info['UserInfo'][i]['Username']]:
                                        self.user_info['Account Info']['Mutual friends'][t][self.all_user_info['UserInfo'][i]['Username']].append(self.all_user_info['UserInfo'][i]['Account Info']['All Friends'][x])
                    
                    if not user in self.user_info['Account Info']['All Friends']:
                        print(f'You and {self.all_user_info["UserInfo"][i]["Account Info"]["DispName"]}({user}) are not friends :c\n')
                        add_as_friend = int(input('Add as friend?[0 yes, 1 no] > '))

                        if add_as_friend == 0:
                            if self.user_info['Username'] not in self.all_user_info['UserInfo'][i]['Account Info']['All Friends']:
                                self.all_user_info['UserInfo'][i]['Account Info']['Pending Adds'].append(self.user_info['Username'])
                    else:
                        print(f'You and {self.all_user_info["UserInfo"][i]["Account Info"]["DispName"]}({user}) are friends!\n')
                    for d in self.all_user_info['UserInfo'][i]['Account Info']['Mutual friends']:
                        if self.user_info['Username'] in d:
                            print(f'You and {self.all_user_info["UserInfo"][i]["Account Info"]["DispName"]}({user}) have {len(self.all_user_info["UserInfo"][i]["Account Info"]["Mutual friends"])} mutal friend(s)\nMutual Friends:\n---------------')
                            for i in range(len(d[self.user_info['Username']])):
                                print('\t', i + 1, ' > ', d[self.user_info['Username']][i], '\n')
                    break
        else:
            self.__profile__()

    def __start__(self):
        """ KEEP THE PROGRAM RUNNING """
        while self.logged_in:
            os.system('clear')
            print(f'''{Fore.YELLOW}
░█████╗░███████╗███████╗██████╗░██████╗░░█████╗░███╗░░██╗██████╗░
██╔══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗████╗░██║██╔══██╗
██║░░██║█████╗░░█████╗░░██████╦╝██████╔╝███████║██╔██╗██║██║░░██║
██║░░██║██╔══╝░░██╔══╝░░██╔══██╗██╔══██╗██╔══██║██║╚████║██║░░██║
╚█████╔╝██║░░░░░██║░░░░░██████╦╝██║░░██║██║░░██║██║░╚███║██████╔╝
░╚════╝░╚═╝░░░░░╚═╝░░░░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░

░██████╗███╗░░██╗░█████╗░██████╗░░░██╗██╗░░░██╗░░███╗░░░░░░█████╗░░░░░░███╗░░██╗░░
██╔════╝████╗░██║██╔══██╗██╔══██╗░██╔╝██║░░░██║░████║░░░░░██╔══██╗░░░░████║░░╚██╗░
╚█████╗░██╔██╗██║███████║██████╔╝██╔╝░╚██╗░██╔╝██╔██║░░░░░██║░░██║░░░██╔██║░░░╚██╗
░╚═══██╗██║╚████║██╔══██║██╔═══╝░╚██╗░░╚████╔╝░╚═╝██║░░░░░██║░░██║░░░╚═╝██║░░░██╔╝
██████╔╝██║░╚███║██║░░██║██║░░░░░░╚██╗░░╚██╔╝░░███████╗██╗╚█████╔╝██╗███████╗██╔╝░
╚═════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░░░░░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░╚════╝░╚═╝╚══════╝╚═╝░░{Fore.RESET}\n\n\t\t{Back.WHITE}{Fore.BLACK}\t:)        👻  𝓛𝓸𝓰𝓰𝓮𝓭 𝓘𝓷 𝓐𝓼 {self.display_name}👻        (:\t{Style.RESET_ALL}\n
\t\t\t1. See Profile
\t\t\t2. See all friends
\t\t\t3. Add a user
\t\t\t4. Search for a user
\t\t\t5. Logout''')

            choice = int(input('\t\t\t>> '))

            if choice == 1:
                self.__profile__()

                input('PRESS [enter] TO CONTINUE.')
            if choice == 2:
                self._all_friends_()

                input('PRESS [enter] TO CONTINUE.')
            if choice == 3:
                username = input("User to add: ")
                self.__add_user__(username)

                input('PRESS [enter] TO CONTINUE.')
            if choice == 4:
                user = input('Username: ')

                self._user_exists_(user)

                input('PRESS [enter] TO CONTINUE.')
            if choice == 5:
                self.cursor.execute(
                    f'UPDATE UserInfo SET logged_in = 1 WHERE username = "{self.user_info["Username"]}"'
                )
                self.db.commit()
                os.system('clear')
                print(
                    f'''{Fore.YELLOW}
░█████╗░███████╗███████╗██████╗░██████╗░░█████╗░███╗░░██╗██████╗░
██╔══██╗██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗████╗░██║██╔══██╗
██║░░██║█████╗░░█████╗░░██████╦╝██████╔╝███████║██╔██╗██║██║░░██║
██║░░██║██╔══╝░░██╔══╝░░██╔══██╗██╔══██╗██╔══██║██║╚████║██║░░██║
╚█████╔╝██║░░░░░██║░░░░░██████╦╝██║░░██║██║░░██║██║░╚███║██████╔╝
░╚════╝░╚═╝░░░░░╚═╝░░░░░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░

░██████╗███╗░░██╗░█████╗░██████╗░░░██╗██╗░░░██╗░░███╗░░░░░░█████╗░░░░░░███╗░░██╗░░
██╔════╝████╗░██║██╔══██╗██╔══██╗░██╔╝██║░░░██║░████║░░░░░██╔══██╗░░░░████║░░╚██╗░
╚█████╗░██╔██╗██║███████║██████╔╝██╔╝░╚██╗░██╔╝██╔██║░░░░░██║░░██║░░░██╔██║░░░╚██╗
░╚═══██╗██║╚████║██╔══██║██╔═══╝░╚██╗░░╚████╔╝░╚═╝██║░░░░░██║░░██║░░░╚═╝██║░░░██╔╝
██████╔╝██║░╚███║██║░░██║██║░░░░░░╚██╗░░╚██╔╝░░███████╗██╗╚█████╔╝██╗███████╗██╔╝░
╚═════╝░╚═╝░░╚══╝╚═╝░░╚═╝╚═╝░░░░░░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░╚════╝░╚═╝╚══════╝╚═╝░░{Fore.RESET}\n\n\t\t\t{Fore.BLACK}{Back.WHITE}:)        👻  𝓒𝓸𝓶 𝓮 𝓑𝓪𝓬𝓴 𝓐𝓰𝓪𝓲𝓷,{self.display_name}! 👻        (:\n{Style.RESET_ALL}'''
                )

                # Update all_user_info, then write it to the json file
                self.all_user_info['UserInfo'][self.index].update(self.user_info)

                with open('user_info.json', 'w') as file:
                    file.write(
                        json.dumps(self.all_user_info,
                            indent=2,
                            sort_keys=False
                        ))
                    file.close()

                if self.user_score < self.user_info['Account Info']['Score']:
                    print(
                        f'Your score went up: {self.user_info["Account Info"]["Score"] - self.user_score}\n'
                    )
                if self.total_friends < self.user_info['Account Info'][
                        'Friends']:
                    print(
                        f'You gained {self.user_info["Account Info"]["Friends"] - self.total_friends} friend(s) today!\n'
                    )
                if self.user_score == self.user_info['Account Info'][
                        'Score'] and self.total_friends == self.user_info[
                            'Account Info']['Friends']:
                    print(
                        "Maybe next time you'll gain some friends, and get that score up!"
                    )

                self.__profile__()  # Show the user there profile before exiting
                break
        else:
            print('[ERR]: User not logged in :/')