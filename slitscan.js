const async = require('async');
const sharp = require('sharp');
const path = require('path');
const sprintf = require('sprintf-js').sprintf;

module.exports = ({ imagePaths, outputDir, step }) => {

      let height;
      let tileWidth;
      let slitIndex = 0;
      let tileImage;
      let extractColumn;
      
      let slitWidth = step;

      let lastIndexSaved = -1;
      const saveNextTileImage = () => {
            const tileIndex = ++lastIndexSaved;
            const outputPath = path.join(outputDir, sprintf('tile-%05d.png', tileIndex));
            
            tileImage
                  .toFile(outputPath, (err, info) => {
                        if(err) {
                              console.error('toFile errored: ', err);
                              reject(err);
                        }
                        else {
                              console.log('Saved ' + outputPath);
                        }
                  });
      };

      const copyNextSlitToMural = image => new Promise((resolve, reject) => {
            
            const muralColumn = slitIndex * slitWidth;
            const tileColumn = muralColumn % tileWidth;
            console.log(tileColumn + ' / ' + tileWidth);

            if(tileColumn === 0) {
                  // save current tile if exists
                  if(slitIndex !== 0) {
                        saveNextTileImage();
                  }
                  
                  // create new tile
                  tileImage = sharp({
                        create: {
                              width: tileWidth,
                              height: height,
                              channels: 4,
                              background: { r: 255, g: 255, b: 255, alpha: 0 }
                        }
                  });
            }
            
            image
                  .extract({left: extractColumn, top: 0, width: slitWidth, height: height})
                  .toBuffer((err, buffer, info) => {
                        if(err) {
                              reject(err);
                        }
                        else {
                              // console.log('pasting to ', {tileColumn});
                              tileImage = tileImage
                                    .overlayWith(buffer, {
                                          top: 0,
                                          left: tileColumn
                                          // left: 0
                                    })
                                    .png()
                                    .toBuffer((err, buffer, info) => {
                                          if(err) {
                                                reject(err);
                                          }
                                          else {
                                                tileImage = sharp(buffer);
                                                slitIndex = slitIndex + 1;
                                                resolve();
                                          }
                                    });
                        }

                  });
      });

      async.eachSeries(imagePaths, (imagePath, callback) => {
            const image = sharp(imagePath);
            image
                  .metadata()
                  .then(metadata => {
                        // console.log(metadata.height);
                        if(!height) {
                              height = metadata.height;
                              tileWidth = Math.ceil(height / slitWidth) * slitWidth;
                              // tileWidth = 50;
                              // extractColumn = Math.round(metadata.width / 2);
                              extractColumn = 0;
                              console.log('height = ' + height);
                        }
                        copyNextSlitToMural(image)
                        .then(() => {
                              callback();
                        })
                        .catch(err => {
                              throw err;
                        });
                  })
                  .catch(err => {
                        console.error(imagePath, ':', err);
                        callback();
                  });
      }, err => {
            saveNextTileImage();
      });
};

