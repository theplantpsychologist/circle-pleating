# circle-pleating
It bridges the gap between circle packing and box pleating; thus, circle pleating. 

Instructions to use:
1. Use Robert Lang's Treemaker (v5) to input your tree, and scale everything. You can download treemaker here: https://langorigami.com/article/treemaker/ You can use treemaker to build a crease pattern, but it's not necessary. Make sure to save your .tmd5 file.
2. Run the circle-pleating program. There will be a button to "Open Treemaker file." Click that, and select your .tmd5 file. 
  If you generated a cp with treemaker, it will show up in the square on the left. You can use this program to export the cp as .cp, so you can further edit the cp in orihime or oripa.
3. Regardless of whether treemaker generated a cp, you can click "approximate to bp," as long as treemaker found a valid packing. You may see that there are overlapping flaps, so increase the grid size until they go away or you have a "comfortable" grid size. If you need to lower the grid size, you can click on "approximate to bp" again.
4. There will be some flaps that need pythagorean stretches--after all, that's the whole concept of this conversion from circle packing to boxpleating. Sometimes the generated pythas will be a bit buggy; you can calculate the pythas one at a time using this calculator, https://github.com/theplantpsychologist/Pytha-calculator, although it's almost the same code so i doubt you'll get any different results.
5. You can expand and shrink flaps as necessary, or move them around, or change the grid size as you see fit. Clicking "reset layout" will approximate everything as close to treemaker's as possible, on the current grid size.
6. when you're done, you can export the cp as a .cp file, so you can further modify it in orihime or oripa
