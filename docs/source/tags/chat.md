---
title: Chat
type: tags
hide_menu: true
order: 302
meta_title: Chat Tag for Conversational Transcripts
meta_description: Display and extend chat transcripts; optionally request assistant replies from an LLM. Supports message editing controls and min/max limits.
---

The `Chat` tag displays a conversational transcript and lets annotators extend it by adding new messages:

![Screenshot](/images/tags/chat.png)

Use with the following data types: JSON array of message objects

!!! error Enterprise
    This tag is only available for Label Studio Enterprise and Starter Cloud users. 


### Use with an LLM

Optionally, the tag can request automatic replies from an LLM. 

To use an LLM, you need to do two things:

1. Add a model provider API key to your organization.  

2.  Once you have added an API key for a model provider, set the `llm` attribute on the `<Chat>` tag to the model you want to use. 

    The `llm` attribute must use the format `<provider>/<model>`. For example, `llm="openai/gpt-5"`. 

!!! note
    Starter Cloud users have limited access to the LLM feature for chats. 

    In Starter Cloud, you cannot add model providers. However, you will have access to out-of-the-box OpenAI models with $5.00 in credits for testing. If you want to add your own models and use interactive chats more extensively, you can [upgrade to Enterprise](https://humansignal.com/pricing/). 

### Editing messages

You can allow annotators to edit the messages that they enter and, if applicable, responses from the LLM. 

Set the `editable` parameter to `"true"` or to a list of roles that should be editable. To edit a message, hover over it to view the edit icon.

Annotators cannot edit messages from the imported task data.  

![Screenshot](/images/tags/chat-edit.png)

{% insertmd includes/tags/chat.md %}

## Examples

### Example `<Chat>` tag

The following labeling configuration is the most basic implementation of the Chat tag. Adding a self-referencing `toName` paramenter allows you to use it without any other control tags. 

This labeling configuration would allow an annotator to submit messages from different roles that they select in a drop down message. 

```xml
<View>
  <Chat name="chat" value="$chat" toName="chat" />
</View>
```

You can extend this configuration by allowing auto-replies from an LLM and adding control tags to evaluate the messages, as seen in the example below. 

### Example labeling config

Evaluate assistant responses:

```xml
<View>
  <Style>
    .htx-chat{flex-grow:1}
    .htx-chat-sidepanel{flex:300px 0 0;display:flex;flex-direction:column;border-left:2px solid #ccc;padding-left:16px}
  </Style>
  <View style="display:flex;width:100%;gap:1em">
    <Chat name="chat" value="$chat" llm="openai/gpt-4.1-nano" minMessages="4" maxMessages="10" editable="true" />
    <View className="htx-chat-sidepanel">
      <View style="position:sticky;top:14px">
        <!-- Invitation/explanation on how to evaluate -->
        <View visibleWhen="no-region-selected">
          <Text name="_3" value="Click on a message to rate specific parts of the conversation"/>
        </View>
        <!-- Evaluate assistant messages -->
        <View visibleWhen="region-selected" whenRole="assistant">
          <Text name="_1" value="Rate the response" />
          <Rating name="response_rating" toName="chat" perRegion="true" />
        </View>
      </View>
      <!-- Evaluate the whole conversation -->
      <View style="margin-top:auto;height:130px">
        <Header size="4">Overall quality of this conversation</Header>
        <Rating name="rating" toName="chat" />
      </View>
    </View>
  </View>
</View>
```

### Example input data

!!! attention
    The chat messages that you import are not selectable. This means that you cannot edit them or apply annotations (ratings, choices, etc) to them. 

    You can only select and annotate messages that are added to the chat by an annotator or that are imported as predictions. 

The example JSON input data below is called in the `value="$chat"` parameter. 

- `role`    — speaker identifier; supported roles: `user`, `assistant`, `system`, `tool`, `developer`
- `content` — message text


```json
{
  "data": {
    "chat": [
        {
            "role": "user",
            "content": "Start with a kick-off message to validate the quality of it based on further conversation"
        },
        {
            "role": "assistant",
            "content": "A response from the LLM"
        }
    ]
  }
}
```

To work with a blank chat and have your annotator add all messages, simply import:

```json
{
  "data": {
    "chat": []
  }
}
```