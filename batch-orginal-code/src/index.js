const express = require("express");
const bodyParser = require("body-parser");
const multer = require("multer");
const axios = require("axios");
const { v4: uuidv4 } = require("uuid");
const cors = require("cors");
const fs = require("fs");
const FormData = require("form-data");
const logger = require("./logger"); // <-- Import logger
const utils = require("./utils.js");

const app = express();
app.disable("x-powered-by");

app.use(cors({ origin: true }));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const port = utils.port;
const burl = utils.url;
let base_url = `${burl}/`;

let delay = 150;
const requestList = [];
const translateRequestList = [];
let myMap = new Map();
let myTranslateMap = new Map();

const memoryStorage = multer.memoryStorage({
  limits: { fileSize: 1024 * 1024 * 8 },
});
const upload = multer({
  storage: memoryStorage,
  limits: { fileSize: 1024 * 1024 * 8 },
});

app.get("/", (req, res) => {
  res.send("hello world");
});

app.post("/transcribe", upload.single("audio"), (req, res) => {
  try {
    const id = uuidv4();
    const audio = req.body.audio
      ? req.body.audio
      : Buffer.from(req.file.buffer).toString("binary");
    const text = req.body.text;
    const isByteArray = req.body.isByteArray || "True";
    const LK = req.body.LK || "None";
    const isKeyAndIvInJson = req.body.isKeyAndIvInJson || "True";
    const device = req.body.device || "None";
    const lang = req.body.lang || "en";

    if (LK !== "None") process.env.LK = LK;
    const LCK = process.env.LK || "None";

    const requestData = {
      audio,
      id,
      text,
      isByteArray,
      LCK,
      isKeyAndIvInJson,
      device,
      lang,
    };

    requestList.push(requestData);
    myMap.set(id, res);
    logger.info("Received transcribe request: %s", id);
  } catch (err) {
    logger.error("Error in /transcribe: %s", err.stack || err.message);
    res.status(500).send("Internal Server Error");
  }
});

function processRequests() {
  try {
    if (requestList.length > 0) {
      const batch = [];
      const n = requestList.length;

      for (let j = 0; j < Math.min(n, 8); j++) {
        const item = requestList.shift();
        batch.push(item);
      }

      const requestConfig = {
        method: "post",
        url: `${base_url}transcribe`,
        headers: { "Content-Type": "application/json" },
        data: { data: JSON.stringify(batch) },
      };

      axios(requestConfig)
        .then((response) => {
          logger.info("Transcribe batch processed: %d items", batch.length);
          for (const elem of response.data) {
            const socket = myMap.get(elem.uid);
            if (socket) {
              socket.send(elem);
              myMap.delete(elem.uid);

            }

          }
        })
        .catch((err) => {
          logger.error("Transcribe request error: %s", err.stack || err.message);
        });
    }
  } catch (error) {
    logger.error("Transcribe batch failed: %s", error.stack || error.message);
  } finally {
    setTimeout(processRequests, delay);
  }
}

processRequests();

app.post("/translate", upload.single("audio"), (req, res) => {
  try {
    const id = uuidv4();
    const audio = req.body.audio
      ? req.body.audio
      : Buffer.from(req.file.buffer).toString("binary");
    const text = req.body.text;
    const isByteArray = req.body.isByteArray || "True";
    const LK = req.body.LK || "None";
    const isKeyAndIvInJson = req.body.isKeyAndIvInJson || "True";
    const lang = req.body.lang || "en";
    const device = req.body.device || "None";

    if (LK !== "None") process.env.LK = LK;
    const LCK = process.env.LK || "None";

    const requestData = {
      audio,
      id,
      text,
      isByteArray,
      LCK,
      isKeyAndIvInJson,
      lang,
      device,
    };

    translateRequestList.push(requestData);
    myTranslateMap.set(id, res);
    logger.info("Received translate request: %s", id);
  } catch (err) {
    logger.error("Error in /translate: %s", err.stack || err.message);
    res.status(500).send("Internal Server Error");
  }
});

function translateProcessRequests() {
  try {
    if (translateRequestList.length > 0) {
      const batch = [];
      const n = translateRequestList.length;

      for (let j = 0; j < Math.min(n, 1); j++) {
        const item = translateRequestList.shift();
        batch.push(item);
      }

      const requestConfig = {
        method: "post",
        url: `${base_url}translate`,
        headers: { "Content-Type": "application/json" },
        data: { data: JSON.stringify(batch) },
      };

      axios(requestConfig)
        .then((response) => {
          logger.info("Translate batch processed: %d items", batch.length);
          for (const elem of response.data) {
            const socket = myTranslateMap.get(elem.uid);
            if (socket) {
              socket.send(elem);
              myTranslateMap.delete(elem.uid);
            }
          }
        })
        .catch((err) => {
          logger.error("Translate request error: %s", err.stack || err.message);
        });
    }
  } catch (error) {
    logger.error("Translate batch failed: %s", error.stack || error.message);
  } finally {
    setTimeout(translateProcessRequests, delay);
  }
}

translateProcessRequests();

app.listen(port, () => {
  logger.info(`Server is listening on port ${port}`);
});
