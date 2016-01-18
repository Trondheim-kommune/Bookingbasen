Running Buster Tests
====================

1. install Node (if not installed): see http://docs.busterjs.org/en/latest/getting-started/
2. install buster.js (npm install -g buster)
3. from this dir, run buster-server &
4. point your favourite browser to localhost:1111
5. "capture browser"
6. run tests with "buster test"

(on linux, use kill %% to kill buster-server when finished)

alternative (for easier debugging in browser):
--------------
1. go to the directory with the tests
2. run buster-static (possible add --tests <test.js> as argument)
3. open localhost:8283 in web browser
