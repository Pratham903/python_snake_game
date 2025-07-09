// Timepass JS code: Simple timer that logs time every second
let seconds = 0;
setInterval(() => {
  seconds++;
  console.log(`Time passed: ${seconds} second(s)`);
}, 1000);
