#!/usr/bin/make -f

PKGNAM := mx-updater

PKG_VERSION ?=

BLDROOT  := $(abspath $(CURDIR)/..)
BUILD    := ././build
PO_DIR   := ./po
XDGDIR   := ../xdg

LCMSGS := LC_MESSAGES/$(PKGNAM).mo

DESKTOP_IN  := $(wildcard $(XDGDIR)/*.desktop)
DESKTOP     := $(addprefix $(BUILD)/xdg/,$(notdir $(DESKTOP_IN)))

POLICY_DIR  := ../polkit/actions
POLICY_IN   := $(wildcard $(POLICY_DIR)/*.policy)
POLICY_OUT  := $(addprefix $(BUILD)/policy/,$(notdir $(POLICY_IN)))
POLICY_PO   := $(BUILD)/po-policy

ifneq ($(strip $(LINGUAS)),)
  LINGUAS := $(sort $(LINGUAS))
  $(file >$(PO_DIR)/LINGUAS)
  $(foreach po,$(LINGUAS),$(file >>$(PO_DIR)/LINGUAS,$(po)))
else ifneq ($(wildcard $(PO_DIR)/LINGUAS),)
  LINGUAS := $(sort $(strip $(shell grep '^[[:space:]]*[a-z]' $(PO_DIR)/LINGUAS)))
else
  LINGUAS := $(sort $(basename $(notdir $(wildcard $(PO_DIR)/*.po))))
  $(foreach po,$(LINGUAS),$(file >>$(PO_DIR)/LINGUAS,$(po)))
endif

LOCALE := $(addprefix $(BUILD)/locale/,$(addsuffix /$(LCMSGS),$(LINGUAS)))

HELP_PO_DIR  := ./help-po
HELP_MD      := $(abspath $(BLDROOT)/share/doc/mx-updater/help.md)
HELP_DOC_DIR := $(abspath $(BLDROOT)/share/doc/mx-updater)
HELP_LCMSGS  := LC_MESSAGES/mx-updater-help.mo

ifneq ($(wildcard $(HELP_PO_DIR)/LINGUAS),)
  HELP_LINGUAS := $(sort $(strip $(shell grep '^[[:space:]]*[a-z]' $(HELP_PO_DIR)/LINGUAS)))
else
  HELP_LINGUAS := $(sort $(basename $(notdir $(wildcard $(HELP_PO_DIR)/*.po))))
endif

HELP_LOCALE := $(addprefix $(BUILD)/locale/,$(addsuffix /$(HELP_LCMSGS),$(HELP_LINGUAS)))

LAUNCHER_PO_DIR  := ./mx-launcher-l10n-po
LAUNCHER_LCMSGS  := LC_MESSAGES/mx-launcher-l10n.mo

ifneq ($(wildcard $(LAUNCHER_PO_DIR)/LINGUAS),)
  LAUNCHER_LINGUAS := $(sort $(strip $(shell grep '^[[:space:]]*[a-z]' $(LAUNCHER_PO_DIR)/LINGUAS)))
else
  LAUNCHER_LINGUAS := $(sort $(basename $(notdir $(wildcard $(LAUNCHER_PO_DIR)/*.po))))
endif

LAUNCHER_LOCALE := $(addprefix $(BUILD)/locale/,$(addsuffix /$(LAUNCHER_LCMSGS),$(LAUNCHER_LINGUAS)))

all: clean locale desktop policy help

locale: $(LOCALE)

$(BUILD)/locale/%/$(LCMSGS): $(PO_DIR)/%.po
	@mkdir -p $(BUILD)/locale/$*/LC_MESSAGES
	@echo "  " $@
	@msgfmt $< -o $@

desktop: $(DESKTOP)

$(BUILD)/xdg/%.desktop: $(XDGDIR)/%.desktop
	@mkdir -p $(BUILD)/xdg
	@echo "  " $@
	msgfmt --desktop --template $< -d $(PO_DIR) -o $@
	@sed -i '/^#/d' $@

policy: $(POLICY_OUT)

$(POLICY_PO)/LINGUAS: $(PO_DIR)/LINGUAS $(wildcard $(PO_DIR)/*.po)
	@mkdir -p $(POLICY_PO)
	@sort -r $(PO_DIR)/LINGUAS > $@
	@for po in $(abspath $(PO_DIR))/*.po; do ln -sf "$$po" $(POLICY_PO)/; done

$(BUILD)/policy/%.policy: $(POLICY_DIR)/%.policy $(POLICY_PO)/LINGUAS
	@mkdir -p $(BUILD)/policy
	@echo "  " $@
	GETTEXTDATADIRS=../polkit/ msgfmt --xml --template=$< -d $(POLICY_PO) -o $@
	@sed -i '/<!-- TRANSLATORS:/d' $@

# Compile help po files to mo (domain: mx-updater-help)
$(BUILD)/locale/%/$(HELP_LCMSGS): $(HELP_PO_DIR)/%.po
	@mkdir -p $(BUILD)/locale/$*/LC_MESSAGES
	@echo "  " $@
	@msgfmt $< -o $@

# Compile launcher po files to mo (domain: mx-launcher-l10n)
$(BUILD)/locale/%/$(LAUNCHER_LCMSGS): $(LAUNCHER_PO_DIR)/%.po
	@mkdir -p $(BUILD)/locale/$*/LC_MESSAGES
	@echo "  " $@
	@msgfmt $< -o $@

# Generate English help.html and all translated help_<lang>.html from help.md.
# Main mo files ($(LOCALE)) are needed for token resolution in every language.
help: $(HELP_MD) $(LOCALE) $(HELP_LOCALE) $(LAUNCHER_LOCALE)
	@# English -- identity translation, tokens resolved from source text
	python3 build-help-html $(HELP_MD) $(HELP_DOC_DIR)/help.html \
	  $(abspath $(BUILD)/locale) ''
	@if [ -n "$(PKG_VERSION)" ]; then \
	  sed -i "s|@VERSION@|$(PKG_VERSION)|g" $(HELP_DOC_DIR)/help.html; \
	fi
	@# Translated versions
	@for lang in $(HELP_LINGUAS); do \
	  dest=$(HELP_DOC_DIR)/help_$${lang}.html; \
	  python3 build-help-html $(HELP_MD) $$dest \
	    $(abspath $(BUILD)/locale) $$lang; \
	  if [ -n "$(PKG_VERSION)" ]; then \
	    sed -i "s|@VERSION@|$(PKG_VERSION)|g" $$dest; \
	  fi; \
	  lang_img_dir=$(HELP_DOC_DIR)/img/$${lang}; \
	  [ -d "$$lang_img_dir" ] || continue; \
	  for img in $(HELP_DOC_DIR)/img/*.jpg; do \
	    base=$$(basename "$$img"); \
	    [ -f "$$lang_img_dir/$$base" ] || continue; \
	    sed -i "s|src=\"img/$$base\"|src=\"img/$${lang}/$$base\"|g" $$dest; \
	  done; \
	done
	@# Launcher mo files were needed only for help HTML generation above;
	@# they are provided at runtime by the mx-launcher-l10n package.
	@rm -f $(LAUNCHER_LOCALE)

# Manual target: extract pot from help.md, then upload to Transifex.
# Not run during debuild; run manually whenever help.md is updated.
help-pot: $(HELP_MD)
	python3 help-extract-pot $(HELP_MD) mx-updater-help.pot
	@echo "  mx-updater-help.pot -- upload to Transifex when ready"

clean:
	-@rm  -f $(DESKTOP)
	-@rm -rf $(BUILD)
	-@rm  -f $(HELP_DOC_DIR)/help.html
	-@rm  -f $(HELP_DOC_DIR)/help_*.html

.PHONY: all clean locale desktop policy help help-pot
