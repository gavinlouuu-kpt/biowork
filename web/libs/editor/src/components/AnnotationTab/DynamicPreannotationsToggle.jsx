import { inject, observer } from "mobx-react";
import { useEffect } from "react";
import { Space } from "../../common/Space/Space";
import { Toggle } from "@humansignal/ui";
import ToolsManager from "../../tools/Manager";
import { Block, Elem } from "../../utils/bem";
import "./DynamicPreannotationsToggle.scss";

export const DynamicPreannotationsToggle = inject("store")(
  observer(({ store }) => {
    const enabled = store.hasInterface("auto-annotation") && !store.forceAutoAnnotation;

    useEffect(() => {
      if (!enabled) store.setAutoAnnotation(false);
    }, [enabled]);

    return enabled ? (
      <Block name="dynamic-preannotations">
        <Elem name="wrapper">
          <Space spread>
            <Toggle
              checked={store.autoAnnotation}
              onChange={(e) => {
                const checked = e.target.checked;

                store.setAutoAnnotation(checked);

                if (checked) {
                  // when enabling auto-annotation prefer smart tools for managers with an active selection
                  ToolsManager.allInstances().forEach((inst) => {
                    if (inst.findSelectedTool()) inst.selectSmartDefault();
                  });
                } else {
                  // when disabling auto-annotation, only revert managers that currently have a smart tool selected
                  ToolsManager.allInstances().forEach((inst) => {
                    if (inst.findSelectedTool()?.dynamic === true) inst.selectDefault();
                  });
                }
              }}
              label="Auto-Annotation"
            />
          </Space>
        </Elem>
      </Block>
    ) : null;
  }),
);
