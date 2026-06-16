const admin = require("firebase-admin");

// จัดระเบียบคีย์ใหม่ล่าสุดของบาส (ID: 203615ab...) แยกเป็นแถวเพื่อความชัวร์ ไม่ให้เว้นวรรคหลุดซ้ำรอยเดิม
const privateKeyLines = [
  "-----BEGIN PRIVATE KEY-----",
  "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCZsepZJy1xNU79",
  "stLq1jVdeFsJUf/54j45gEYKffO6IfUuJaDeJTzrw8uDrYJwxmOtkO2Mjnz49kPh",
  "it6n3dqmlZkkp4JYtVGDDETDHTr2oq+hh3C7hs2BcaK04dpx/0RF+P1HDEsxPAHO",
  "J0vOgiNjdyrWHd8zXAvpG2CpazwF2IK8ul+PhCAOMb98DSR8CZ7QibLmoSZbGTc0",
  "Et3aA5/lWvXSha8ASlFeGh++Xyc5cuJ1v6dA7lnb22YkCMpFTGNDde5j0XLfkfOQ",
  "fe2QpioyJOrspHuzrbFZqvajGBWUmlsGTu4lYgtHaWjbPhwB2g/4btJPusOA6AdW",
  "rwPL4ZefAgMBAAECggEAOlo0MVkQhbTJosSsE4D0jeJOHgHF/+eH3Gj5Lq6XRInz",
  "/mtG4lCdCp4xvHK53XtVCObHaeAHTrahGxaQZodypmCR3jrC4E8m/WxBBxsn8c/e",
  "gqNbh7csewLb1XUSbMmP8EkSUFE4kx7HSK/eti7upKrv1o9M2MEPvJcqYehWx5jP",
  "mnLA4q11JOinv6sGpe+es5CROnnWaXDyUlZ4XWJY2jefte59UYUzBckcXLn6y0zM",
  "yiS9crCwASZaEnqXbh1IWe8+KCzORW+xk7DHuy+W59R94NhKmWEPL0PFm7hnwhHG",
  "gva+3ssCWBLUAY3Q4Tn+tkMx+LJzjH/vG9P+RodpoQKBgQDHrBKLz7CuQRCaghGg",
  "rAaHVg/9bRL9P9WNAILbeEajxx3uKmlOLXKYKrtbr2pYDwHZo2mG8q4RT8C1Ns1I",
  "ovbWtN0GNJeHcHQ9PGxUW0JTxvrOf/Q++rRTb/v4GL60yJzreCH6LTuMA+DljMBU",
  "YAqLnrsO6DElIVbdNQ8U3vIaVwKBgQDFDXZjHbH862FBiMJZL/skc00xQY3Se/Z7",
  "hO/ZroZUXhraH8PH5PH5aWeCddFcGx2ia478KFN5hcNJmbP8g3DJ0rt5wMdnQ8Kr",
  "KU5JTtSO4L+WFVY3ztngx64piADRzTAxjIQ46E6m55+uk4zL8UqB0Rd1Abe1eLz6",
  "MGiJ4vAv+QKBgA+SXNPoe5frXRcfo65LHCs7y/1wnzV+3/GiI5JoG+Iz6iKjzhiZ",
  "tMEnO/tXf8ykRvmpI9axYF/bP2Uig/nxM5zk+AO+4D5gx7/q0Wv2vgJ4lyC5m9u5",
  "g4yqRBVCIMVKi+pVMRkoo+c0ejqMsociAlCHLYFpHEQQCI0x0R5IkMr7AoGBAIQI",
  "7j+hoSaQbV1lDpyGKuiUna+YdjgIOfMv8yrP51BWsfVf/WZOgNiXCPWAjmUCAkxX",
  "d7p8Jtqxh1YkuFZFmGiTXG1LgBEwdRsNFVjHimOmMpmU+G1ym8ki4w8PA0WREG7S",
  "bBHT7welAfkPAvOQXVU4zlfna7ocCbw2fYWO21O5AoGACzICVMDNTVPOMgzEiEPf",
  "UO5vBL1xiYWRSO4+gt+WDb1V3ObdZlRlA/Gkek6xtkwJeZphIza1ItXw0MvaJd1h",
  "Y2eY6y4Z5ZYLF1R8HdQCVkQJ162IAkA9wjzeTrX7JXb3gkNhoMhHUT+rTn/IiTVB",
  "Ostu6lT++fIZqXmuw2SqjCs=",
  "-----END PRIVATE KEY-----"
];

const serviceAccount = {
  type: "service_account",
  project_id: "sooksun-104",
  private_key_id: "203615ab4def5a9218aa2ba27b80bfb9503b2504",
  private_key: privateKeyLines.join("\n"), // นำมาร้อยต่อกันด้วยการขึ้นบรรทัดใหม่ตามมาตรฐาน JWT ของ Google
  client_email: "firebase-adminsdk-fbsvc@sooksun-104.iam.gserviceaccount.com",
  client_id: "101794686310728865878",
  auth_uri: "https://accounts.google.com/o/oauth2/auth",
  token_uri: "https://oauth2.googleapis.com/token",
  auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40sooksun-104.iam.gserviceaccount.com",
  universe_domain: "googleapis.com"
};

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://sooksun-104-default-rtdb.firebaseio.com"
});

console.log("⚡ [SYNAPSE RADAR] Node.js Firebase Connected Successfully!");
