#!/usr/bin/env python3
import json
import os
import subprocess

build_dir = "_build"

def addons():
    dirs = []
    for file in os.listdir("."):
        init = os.path.join(file, "__init__.py")
        if os.path.exists(init):
            dirs.append(file)
    return dirs

def build_all():
    needed = []
    for dir in addons():
        if needs_build(dir):
            needed.append(dir)

    if needed:
        print("linting...")
        lint(needed)
        for dir in needed:
            print("building", dir, "...")
            build(dir)

def needs_build(dir):
    build_ts = last_build_time(dir)
    mod_ts = most_recent_change(dir)
    return mod_ts > build_ts

def build(dir):
    out = target_file(dir)
    if os.path.exists(out):
        os.unlink(out)
    ensure_manifest(dir)
    subprocess.check_call(["7z", "a", "-tzip",
                           "-x!meta.json",
                           "-bso0", # less verbose
                           os.path.join(build_dir, dir+".ankiaddon"),
                           # package folder contents but not folder itself
                           "-w", os.path.join(dir, ".")])

def lint(dirs):
    env=os.environ.copy()
    env["PYTHONPATH"]="../dtop"
    subprocess.check_call([
        "pylint",
        "-j", "0",
        "--rcfile=../dtop/.pylintrc",
        "-f", "colorized",
        "--extension-pkg-whitelist=PyQt5",
    ] + dirs, env=env)

def ensure_manifest(dir):
    manifest_path = os.path.join(dir, "manifest.json")
    if not os.path.exists(manifest_path):
        open(manifest_path, "w").write(json.dumps(dict(package=dir, name=dir)))

def target_file(dir):
    return os.path.join(build_dir, dir+".ankiaddon")

def last_build_time(dir):
    out = target_file(dir)
    try:
        return os.stat(out).st_mtime
    except:
        return 0

def most_recent_change(dir):
    newest = 0

    for dirpath, _, fnames in os.walk(dir):
        for fname in fnames:
            path = os.path.join(dirpath, fname)
            newest = max(newest, os.stat(path).st_mtime)

    return newest

build_all()
print("all done")
