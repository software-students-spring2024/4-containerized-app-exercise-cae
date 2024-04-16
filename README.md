![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)

[![lint-free](https://github.com/software-students-spring2024/4-containerized-app-exercise-cae/actions/workflows/lint.yml/badge.svg)](https://github.com/software-students-spring2024/4-containerized-app-exercise-cae/actions/workflows/lint.yml)

# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

## Description

This project is a image main color palette detector web application working with the following process:
1. The app will take an image from the user's available camera.
2. The image will be sent to the database running in another Docker container within the build.
3. The machine learning client will receive the message from the web app, and will grab the image data from the database.
4. The machine learning client will analyze the image's main color palette, and will output its RBG, HEX and color name.
5. The output color data will be sent back to the database.
6. The web app will receive the feedback message from the machine learning client, and will grab the color data from the database.
7. The grabbed color data will be used in rendering web page template, and thus making the web page display the final result to the user.

## Team members

[Zhongqian Chen (John)](https://github.com/ZhongqianChen) (https://github.com/ZhongqianChen)

[Eric Emmendorfer](https://github.com/ericemmendorfer) (https://github.com/ericemmendorfer)

[Hojong Shim](https://github.com/HojongShim) (https://github.com/HojongShim)

[Ethan Kim](https://github.com/ethanki) (https://github.com/ethanki)

## Instructions

Follow the following steps to run this app:
1. Fully intall Docker on your local machine
2. Open the directory and run the command `docker-compose up --build`
3. The time that this web app start up will be slightly different between each run, and try to run the web page way too fast will result in errors. Thus, please wait until you see the message `mlclient  | Waiting for messages...` inside your terminal to proceed to the next step.
4. Access your `localhost:5000:500` web page at `http://172.20.0.5:5000/` in your web browser, if everything was set up correctly then you should see the web page with the title and a button for image capturing.
5. Click on the `Capture Image` button to capture an image from your device's available camera, remember to allow the web app to access it when your browser prompts you to give permission.
6. Wait for a moment, and the web page will redirect you to another page that will show the analyzed main color of your captured image.

There is no need for any starter data for this web app to run, so follow the above steps correctly and you should be able to use the web app as intended.