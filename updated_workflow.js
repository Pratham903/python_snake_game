// Random 15 lines of JavaScript code for testing
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

const arr = [];
for (let i = 0; i < 10; i++) {
  arr.push(getRandomInt(1, 100));
}

console.log("Random Array:", arr);

const sum = arr.reduce((a, b) => a + b, 0);
console.log("Sum:", sum);

const max = Math.max(...arr);
console.log("Max:", max);

const min = Math.min(...arr);
console.log("Min:", min);
