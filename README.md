# SectionMCPy
python programming based moment curvature analysis for structural sections
## 
Download sectionMCPy from (https://fbs.sh/JunjunGuo/sectionMCPy/sectionMCPySetup.exe)  (windows version)   
## 
[Cite] Guo, Junjun, Chao Chen, Hui Jiang, Penghui Zhang, Xingji Lu, Chen Liang, and Xinzhi Dang. "SectionMCPy: Python programming-based moment-curvature analysis for cross-sections." SoftwareX 31 (2025): 102365.
______
- [Tutorial-1: Circle section example](#Tutorials-1)
- [Tutorial-2: Polygon section example](#Tutorials-2)
______
## Tutorials-1      
### Circle section example
1. Prepare your own section based on the template DXF file (circle_solid.dxf in the current example). The scale factor is 1, and the unit is cm in the template. The border lines are drawn with a layer named "lines", and the reinforcing bars are drawn with layers named "bars_1", "bars_2", etc.  The numbering of the bars must start from 1. Bars in different layers mean having different properties, such as diameter or material. (see Figure 1.1)
2. Then, open the program, click the "fiber mesh" button, and select the working directory. Click the "dxf section" button or the "open database" button. The first selection means conducting new sectional fiber discretization, and the second selection means displaying the generated section fibers that are stored in the database. In the current example, a new analysis is considered, and the "dxf section" button is selected. Enter the parameters based on your section, and use the provided tips to assist with entering parameter values. After input parameters, click the "mesh fiber!" button to discretize the section, and the generated fibers are automatically saved in the database. Moreover, users can also output the generated fibers in txt format by clicking the "output mesh!" button. (see Figure 1.2)
3. Click the "moment curvature analysis" button to conduct moment curvature analysis for the section. Select the "circle" radio button for the current example, and input the necessary parameter values based on the tips. It should be noted that the user rebar materials used in the current example (https://openseespydoc.readthedocs.io/en/latest/index.html) and the material tags correspond to the rebar numbering in the DXF file. Then, click "start analysis!" to conduct moment curvature analysis. (see Figure 1.3)
4. After finishing the analyses, users can switch to the "moment curvature curve" page and the "fiber response" page to check the result figures. (see Figure 1.4)

<img src="https://github.com/Junjun1guo/SectionMCPy/blob/main/circle_solid_1.jpg" width =100% height =100% div align="center">  
<p align="center">Figure 1.1 </p>
<img src="https://github.com/Junjun1guo/SectionMCPy/blob/main/circle_solid_2.jpg" width =100% height =100% div align="center">  
<p align="center">Figure 1.2 </p>
<img src="https://github.com/Junjun1guo/SectionMCPy/blob/main/circle_solid_3.jpg" width =100% height =100% div align="center">  
<p align="center">Figure 1.3 </p>
<img src="https://github.com/Junjun1guo/SectionMCPy/blob/main/circle_solid_4.jpg" width =100% height =100% div align="center">    
<p align="center">Figure 1.4 </p>     

______
## Tutorials-2    
### Polygon section example
1. Prepare your own section based on the template DXF file (polygon_solid.dxf in the current example). The scale factor is 1, and the unit is cm in the template. The border lines are drawn with a layer named "lines", and the reinforcing bars are drawn with layers named "bars_1", "bars_2", etc.  The numbering of the bars must start from 1. Bars in different layers mean having different properties, such as diameter or material. (see Figure 2.1)
2. Then, open the program, click the "fiber mesh" button, and select the working directory. Click the "dxf section" button or the "open database" button. The first selection means conducting new sectional fiber discretization, and the second selection means displaying the generated section fibers that are stored in the database. In the current example, a new analysis is considered, and the "dxf section" button is selected. Enter the parameters based on your section, and use the provided tips to assist with entering parameter values. After input parameters, click the "mesh fiber!" button to discretize the section, and the generated fibers are automatically saved in the database. Moreover, users can also output the generated fibers in txt format by clicking the "output mesh!" button. (see Figure 2.2)
3. Click the "moment curvature analysis" button to conduct moment curvature analysis for the section. Select the "rectangle" radio button for the current example, and input the necessary parameter values based on the tips. Then, click "start analysis!" to conduct moment curvature analysis. (see Figure 2.3)
4. After finishing the analyses, users can switch to the "moment curvature curve" page and the "fiber response" page to check the result figures. (see Figure 2.4)

<img src="https://github.com/Junjun1guo/SectionMCPy/blob/main/polygon_solid_1.jpg" width =100% height =100% div align="center">  
<p align="center">Figure 2.1 </p>
<img src="https://github.com/Junjun1guo/SectionMCPy/blob/main/polygon_solid_2.png" width =100% height =100% div align="center">  
<p align="center">Figure 2.2 </p>
<img src="https://github.com/Junjun1guo/SectionMCPy/blob/main/polygon_solid_3.png" width =100% height =100% div align="center">  
<p align="center">Figure 2.3 </p>
<img src="https://github.com/Junjun1guo/SectionMCPy/blob/main/polygon_solid_4.png" width =100% height =100% div align="center">  
<p align="center">Figure 2.4 </p>
