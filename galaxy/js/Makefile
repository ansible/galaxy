SRC_ROOT = ./galaxy/js
INTERMEDIATE_PATH = ./tmp
OUTPUT_PATH = ./galaxy/static/js

MAIN_SOURCES = apps/main_app.js controllers/main.js services/roles.js services/categories.js services/users.js lib/utilities.js
LIST_SOURCES = angular-slider.min.js apps/list_app.js controllers/list.js services/categories.js services/me.js services/ratings.js services/roles.js services/storage.js services/users.js lib/utilities.js lib/search.js services/related.js lib/paginate.js
ACCOUNTS_SOURCES = services/me.js services/storage.js services/related.js lib/utilities.js controllers/accounts.js apps/accounts_app.js
VENDOR_SOURCES = jquery-1.9.1.js jquery-ui.min.js bootstrap.min.js angular.min.js angular-resource.min.js angular-route.min.js angular-sanitize.min.js angular-cookies.min.js ui-bootstrap-custom-0.7.0.js ui-bootstrap-custom-tpls-0.7.0.js select2.js


.INTERMEDIATE: $(INTERMEDIATE_PATH)/%.concat.js

tmp:
	mkdir tmp

$(INTERMEDIATE_PATH)/vendor.concat.js: tmp
	cat $(addprefix galaxy/js/,$(VENDOR_SOURCES)) > $@

$(INTERMEDIATE_PATH)/list.concat.js: tmp
	cat $(addprefix galaxy/js/,$(LIST_SOURCES)) > $@

$(INTERMEDIATE_PATH)/main.concat.js: tmp
	cat $(addprefix galaxy/js/,$(MAIN_SOURCES)) > $@

$(INTERMEDIATE_PATH)/accounts.concat.js: tmp
	cat $(addprefix galaxy/js/,$(ACCOUNTS_SOURCES)) > $@

js:
	mkdir -p $(OUTPUT_PATH)

$(OUTPUT_PATH)/%.js: $(INTERMEDIATE_PATH)/%.concat.js js
	closure $(CLOSURE_FLAGS) --js $< --js_output_file $@ --language_in=ECMASCRIPT5

$(OUTPUT_PATH)/vendor.js: $(INTERMEDIATE_PATH)/vendor.concat.js js
	cat $< > $@
