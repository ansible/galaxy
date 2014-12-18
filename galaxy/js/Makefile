SRC_ROOT = ./galaxy/js
INTERMEDIATE_PATH = ./tmp
OUTPUT_PATH = ./galaxy/static/js
OUTPUT = main.js accounts.js list.js vendor.js

MAIN_SOURCES = apps/main_app.js directives/main.js controllers/main.js services/roles.js services/categories.js services/users.js lib/utilities.js
LIST_SOURCES = angular-slider.min.js apps/list_app.js controllers/list.js services/categories.js services/me.js services/ratings.js services/roles.js services/storage.js services/users.js lib/utilities.js lib/search.js services/related.js lib/paginate.js
ACCOUNTS_SOURCES = services/me.js services/storage.js services/related.js lib/utilities.js controllers/accounts.js apps/accounts_app.js
VENDOR_SOURCES = jquery-1.9.1.js jquery-ui.min.js bootstrap.min.js angular.min.js angular-resource.min.js angular-route.min.js angular-sanitize.min.js angular-cookies.min.js ui-bootstrap-custom-0.7.0.js ui-bootstrap-custom-tpls-0.7.0.js select2.js


.INTERMEDIATE: $(INTERMEDIATE_PATH)/%.concat.js

tmp:
	mkdir tmp

$(INTERMEDIATE_PATH)/vendor.concat.js: $(addprefix galaxy/js/,$(VENDOR_SOURCES)) tmp
	cat $(addprefix galaxy/js/,$(VENDOR_SOURCES)) > $@

$(INTERMEDIATE_PATH)/list.concat.js: $(addprefix galaxy/js/,$(LIST_SOURCES)) tmp
	cat $(addprefix galaxy/js/,$(LIST_SOURCES)) > $@

$(INTERMEDIATE_PATH)/main.concat.js: $(addprefix galaxy/js/,$(MAIN_SOURCES)) tmp
	cat $< > $@

$(INTERMEDIATE_PATH)/accounts.concat.js: $(addprefix galaxy/js/,$(ACCOUNTS_SOURCES)) tmp
	cat $(addprefix galaxy/js/,$(ACCOUNTS_SOURCES)) > $@

js: $(addprefix $(OUTPUT_PATH)/,$(OUTPUT))

$(OUTPUT_PATH):
	mkdir -p $(OUTPUT_PATH)

define run-closure =
	closure $(CLOSURE_FLAGS) --create_source_map $@.map $(addprefix --js ,$^) --source_map_format=V3 --js_output_file $@ --language_in=ECMASCRIPT5
	@echo "Built $@"
endef

$(OUTPUT_PATH)/main.js: $(addprefix $(CURDIR)/galaxy/js/,$(MAIN_SOURCES))
	$(run-closure)

$(OUTPUT_PATH)/vendor.js: $(INTERMEDIATE_PATH)/vendor.concat.js $(OUTPUT_PATH)
	cat $< > $@
