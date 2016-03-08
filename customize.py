import os
import sys
import crypt
import fileinput

import re

import shutil

mount_device_path = "/dev/loop0"
mount_device_boot_path = "/dev/loop0p1"
mount_device_root_path = "/dev/loop0p2"
mount_root_path = "/media"

pi_uid = 1000
pi_gid = 1000

root_uid = 0
root_gid = 0

shadow_file_path = mount_root_path + "/etc/shadow"
pi_home_dir_path = mount_root_path + "/home/pi"
dot_ssh_dir_path = pi_home_dir_path + "/.ssh"
authorized_keys_file_path = dot_ssh_dir_path + "/authorized_keys"

pi_password = "hansemerkur"
pi_authorized_ssh_keys = [
    "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDjhHGeQ5iw1CxHAH8sXT8QmOqL0JzfpVx4LPfwgoo5ahGzerhwfQ8GL2gs4Z2gPfnnEUnkyRxfORMyaS0GMZZlCVAjzS9jhDk/LPnR577OK+9vcoPjGtdcR0TOr2JQ6MoUUF5Q+Thoed/iBbenhrGsBnspL9HeqCijHP0GBezZnWzx6fggwTuUEFwEFIrVwV55eUS+7lBxqMGa2zsG1A+L/meYvkig+1BTqk9zHoQmcchigOAE9RTy56B9skFDqSF75nxQqoePBDGX0qadnxFnRrSde8rICRpA8pqDuacHS9VdXDjBWy+kujiOQX/CMrN04XrMdpY6bBlTvxkOedrV root@d8e09e32146b",
]

hansemerkur_config_dir_path = mount_root_path + "/usr/share/hansemerkur"
desktop_config_file_path = mount_root_path + "/etc/xdg/pcmanfm/LXDE-pi/desktop-items-0.conf"
keyboard_config_file_path = mount_root_path + "/etc/default/keyboard"
locale_config_file_path = mount_root_path + "/etc/locale.gen"


def generate_password(password):
    return crypt.crypt(password, crypt.mksalt(crypt.METHOD_SHA512))


def change_line(file_path, regex, substitute_string):
    for line in fileinput.input(file_path, inplace=True):
        line = re.sub(r'^pi:.*', substitute_string, line.rstrip())
        print(line)


def create_dir(path, mode, uid, gid):
    os.makedirs(path, mode=mode, exist_ok=True)
    os.chown(path, uid, gid)


def copy_file(src, dst, mode, uid, gid, dir_mode=0o755):
    create_dir(os.path.dirname(dst), dir_mode, uid, gid)
    shutil.copy(src, dst)
    os.chmod(dst, mode)
    os.chown(dst, uid, gid)

# generate and set new password for the user pi:
password_hash = "pi:{}:16840:0:99999:7:::".format(generate_password(pi_password))
change_line(shadow_file_path, "^pi.*", password_hash)

# set authorized_keys for user pi
create_dir(dot_ssh_dir_path, 0o700, pi_uid, pi_gid)

with open(authorized_keys_file_path, mode='w') as file:
    for key in pi_authorized_ssh_keys:
        file.write(key + "\n")
os.chmod(authorized_keys_file_path, 0o600)

# copy ssh key for github repo
copy_file("id_rsa", os.path.join(dot_ssh_dir_path, "id_rsa"), 0o600, pi_uid, pi_gid)
copy_file("id_rsa.pub", os.path.join(dot_ssh_dir_path, "id_rsa.pub"), 0o600, pi_uid, pi_gid)
copy_file(".gitconfig", os.path.join(pi_home_dir_path, ".gitconfig"), 0o644, pi_uid, pi_gid)

# copy wallpaper to pi
copy_file("wallpaper.png", os.path.join(hansemerkur_config_dir_path, "wallpaper.png"), 0o644, root_uid, root_gid)
# set wallpaper as default
copy_file("desktop-items-0.conf", desktop_config_file_path, 0o644, root_uid, root_gid)
# set locale keyboard to de
copy_file("keyboard", keyboard_config_file_path, 0o644, root_uid, root_gid)
# set locale to de_DE
copy_file("locale.gen", locale_config_file_path, 0o644, root_uid, root_gid)