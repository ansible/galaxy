BOWER_COMPONENTS = ./bower_components
NODE_MODULES = ./node_modules

INPUT_PATH = ./galaxy/less
OUTPUT_PATH = ./galaxy/static/css
LESS_OUTPUT = $(OUTPUT_PATH)/galaxy.css
LESSC = $(NODE_MODULES)/.bin/lessc

BOOTSTRAP = $(BOWER_COMPONENTS)/bootstrap/less
SELECT2 = $(BOWER_COMPONENTS)/select2
FONT_AWESOME = $(BOWER_COMPONENTS)/components-font-awesome/less

LESS_LOAD_PATH = $(BOOTSTRAP):$(SELECT2):$(FONT_AWESOME)
LESSCFLAGS = --include-path=$(LESS_LOAD_PATH)

sources = $(INPUT_PATH)/galaxy.less

$(OUTPUT_PATH)/%.css: $(INPUT_PATH)/%.less
	$(LESSC) $(LESSCFLAGS) $< $@

