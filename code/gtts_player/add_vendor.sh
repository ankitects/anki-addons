#!/bin/bash

rm -rf g vendor/gtts
git clone --depth 1 https://github.com/pndurette/gTTS.git g
mv g/gtts vendor
mv g/LICENSE vendor/gtts

rm -rf g
