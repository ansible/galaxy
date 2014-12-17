BOWER_COMPONENTS = ./bower_components
NODE_MODULES = ./node_modules

OUTPUT = galaxy.css galaxy-refresh2014.css style-guide.css

INPUT_PATH = ./galaxy/less
OUTPUT_PATH = ./galaxy/static/css
LESSC = $(NODE_MODULES)/.bin/lessc

VENDOR = bootstrap/less select2 components-font-awesome/less jquery-ui/themes normalize.css emerald/less lesshat/build

space = $(eval) $(eval)
LESS_LOAD_PATH = $(addprefix $(BOWER_COMPONENTS)/,$(VENDOR))
LESSCFLAGS = --include-path=$(subst $(space),:,$(LESS_LOAD_PATH))

$(OUTPUT_PATH)/%.css: $(INPUT_PATH)/*.less $(INPUT_PATH)/**/*.less
	$(LESSC) $(LESSCFLAGS) $(INPUT_PATH)/$*.less $@

css: $(addprefix $(OUTPUT_PATH)/,$(OUTPUT))

