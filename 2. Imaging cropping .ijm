'define input e output
//primeiro input deve ser a origem das imagens grandes invertidas
input="D:\\Projects\\Antartica_Ecopelagos\\Operantar_XLII_Dados\\LOKI_para_fazer\\B01\\LOKI_12023.01\\output2_1360x1024\\"

// primeiro output deve ser a pasta onde serao gravadas as vinhetes
output="D:\\Projects\\Antartica_Ecopelagos\\Operantar_XLII_Dados\\LOKI_para_fazer\\B01\\LOKI_12023.01\\Vinhetes\\"

// segundo input deve ser a raiz LOKI onde estará o arquivo result.txt vazio (CRIE ESSE ARQUIVO)
//input2="D:\\Projects\\Antartica_Ecopelagos\\Operantar_XLI_Dados\\B14\\"

// segundo output deve ser a pasta para as medidas que irao para o TSV
//output2="D:\\Projects\\Antartica_Ecopelagos\\Operantar_XLI_Dados\\B14\\Results\\"

list = getFileList(input);

// this function crops subimages of each organisms in FlowCam images
function crop(input, output, filename) {
	// abre a imagem e localiza as particulas a serem recortadas
	open(input + filename);
	run("Options...", "iterations=1 count=1 black do=Nothing");
	run("Set Measurements...", "area bounding fit shape display redirect=None decimal=2");
//	run("Duplicate...", "title=duplic");
//	run("Find Edges");
//	run("Enhance Local Contrast (CLAHE)", "blocksize=199 histogram=250 maximum=3 mask=*None* fast_(less_accurate)");
//	run("Auto Threshold", "method=Default");
	setThreshold(10, 255, "raw"); setOption("BlackBackground", true);
//	run("Clear Results");
	run("Analyze Particles...", "size=300-Infinity show=Nothing display clear include");
	lines = getValue("results.count");
	xposic = newArray(lines); yposic = newArray(lines); width = newArray(lines); height = newArray(lines);	
	if (lines != 0) {	
		for (v = 0; v < lines; v++) {
			x = getResult("BX", v); xposic[v] = x;
			y = getResult("BY", v); yposic[v] = y;
			w = getResult("Width", v); width[v] = w;
			h = getResult("Height", v); height[v] = h;
		}
		file = substring(filename, 0, lengthOf(filename) - 4); // VERIFICAR E CORRIGIR
	
	// analisa as partículas para encontrar as coordenadas das vinhetes (partículas)
		run("Clear Results");
		run("Set Measurements...", "area mean standard modal min centroid perimeter bounding fit shape feret's median skewness kurtosis display redirect=None decimal=2");
//		contador = 0;

		// separa cada vinhete fazendo um retangulo ao redor e salva na pasta output
		for (z = 0; z < lines; z++) {
			selectWindow(filename);
			makeRectangle(xposic[z], yposic[z], width[z], height[z]);
			run("Duplicate...", "title=Image.tif"); 
			selectWindow("Image.tif"); f = z + 1;
			ID = file + "_" + toString(yposic[z]) + "_" + toString(width[z]) + "_" + toString(height[z]);
//			getRawStatistics(count, mean, min, max, std, histogram);			
			saveAs("Jpeg", output + ID + ".jpg");
			close("Image.tif");
		}
//		selectWindow("Results");
	close(); run("Close All");
	}
}

// macro 2 crop
setBatchMode(true);
for (i = 0; i < list.length; i++)
//	showProgress(i+1, list.length);
    crop(input, output, list[i]);
setBatchMode(false);

close("Results");
