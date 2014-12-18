SRC_ROOT = galaxy/js
OUTPUT_PATH = ./galaxy/static/js
OUTPUT = main.js accounts.js list.js vendor.js

MAIN_SOURCES = $(addprefix $(CURDIR)/$(SRC_ROOT)/,apps/main_app.js directives/main.js controllers/main.js services/roles.js services/categories.js services/users.js services/showcase.js lib/utilities.js)
LIST_SOURCES = $(addprefix $(CURDIR)/$(SRC_ROOT)/,angular-slider.min.js apps/list_app.js controllers/list.js services/categories.js services/me.js services/ratings.js services/roles.js services/storage.js services/users.js lib/utilities.js lib/search.js services/related.js lib/paginate.js)
ACCOUNTS_SOURCES = $(addprefix $(CURDIR)/$(SRC_ROOT)/,services/me.js services/storage.js services/related.js lib/utilities.js controllers/accounts.js apps/accounts_app.js)
VENDOR_SOURCES = $(addprefix $(CURDIR)/$(SRC_ROOT)/,jquery-1.9.1.js jquery-ui.min.js bootstrap.min.js angular.min.js angular-resource.min.js angular-route.min.js angular-sanitize.min.js angular-cookies.min.js ui-bootstrap-custom-0.7.0.js ui-bootstrap-custom-tpls-0.7.0.js select2.js)


tmp:
	mkdir tmp

js: $(addprefix $(OUTPUT_PATH)/,$(OUTPUT))

$(OUTPUT_PATH):
	mkdir -p $(OUTPUT_PATH)

define run-closure =
	closure $(CLOSURE_FLAGS) --create_source_map $@.map $(addprefix --js ,$^) --source_map_format=V3 --js_output_file $@ --language_in=ECMASCRIPT5
	@echo "Built $@"
endef

$(OUTPUT_PATH)/%.js:
	$(run-closure)

$(OUTPUT_PATH)/main.js: $(MAIN_SOURCES)

$(OUTPUT_PATH)/vendor.js: $(VENDOR_SOURCES)

$(OUTPUT_PATH)/accounts.js: $(ACCOUNTS_SOURCES)

$(OUTPUT_PATH)/list.js: $(LIST_SOURCES)
