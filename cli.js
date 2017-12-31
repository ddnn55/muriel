#!/usr/bin/env node

const fs = require('fs');
const argv = require('yargs').argv;
const path = require('path');
const recursive = require("recursive-readdir");

const readdirVisible = (path, cb) => recursive(path, [".*"], function (err, files) {
  cb(err, files);
});

if (argv._[0] === 'slitscan') {
  const slitscan = require('./slitscan');

  const imagesPath = argv.inputImagesPath;
  const outputDir = argv.output;

  const step = (+argv.step) || 20;

  readdirVisible(imagesPath, (err, files) => {
    slitscan({
      imagePaths: files,
      outputDir,
      step
    });
  });

  //  fs.readdir(imagesPath, (err, files) => {
  //   //   console.log('got files:', files);
  //     slitscan({
  //       imagePaths: files.map(file => path.join(imagesPath, file)),
  //       outputDir,
  //       step
  //     });
  //  });
}
