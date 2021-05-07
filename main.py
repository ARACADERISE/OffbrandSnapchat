from src.snap import (
    SetupSnap,
    SnapUi
)

SNAP = SetupSnap()

def main():
    print('''
Offbrand Snapchat(v1.0.1).

1 > Login
2 > Create Account''')

    choice = int(input('>> '))

    if choice == 1:
        username = input('Username: ')
        pass_ = input('Password: ')
        SNAP.login(username, pass_)
    if choice == 2:
        username = input('Create Username: ')
        pass_ = input('Create Password: ')
        
        SNAP.create_user(username, pass_)
        SNAP.create_display_name()

    INFO = SNAP.login_info()
    APP = SnapUi(INFO)
    APP.__start__()

if __name__ == '__main__':
    main()