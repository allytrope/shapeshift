# Compile Nim-JavaScript bindings
nim js -o:bindings.js bindings_js.nim

# Serve the HTML
npx serve .
