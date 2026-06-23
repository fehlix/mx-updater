#!/usr/bin/make -f

PKGNAM := mx-updater

BUILD  := ././build
PO_DIR := ./po
XDGDIR := ../xdg

LCMSGS := LC_MESSAGES/$(PKGNAM).mo

DESKTOP_IN  := $(wildcard $(XDGDIR)/*.desktop)
DESKTOP     := $(addprefix $(BUILD)/xdg/,$(notdir $(DESKTOP_IN)))

POLICY_DIR  := ../polkit/actions
POLICY_IN   := $(wildcard $(POLICY_DIR)/*.policy)
POLICY_OUT  := $(addprefix $(BUILD)/policy/,$(notdir $(POLICY_IN)))

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

all: clean locale desktop policy

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

$(BUILD)/policy/%.policy: $(POLICY_DIR)/%.policy
	@mkdir -p $(BUILD)/policy
	@echo "  " $@
	GETTEXTDATADIRS=../polkit/ msgfmt --xml --template=$< -d $(PO_DIR) -o $@
	@sed -i '/<!-- TRANSLATORS:/d' $@

clean:
	-@rm  -f $(DESKTOP)
	-@rm -rf $(BUILD)

.PHONY: all clean locale desktop policy
