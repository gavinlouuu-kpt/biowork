---
title: Breast Cancer Mammogram Classification
type: templates
category: Community Contributions
cat: community
order: 1000
meta_title: Breast Cancer Mammogram Classification Data Labeling Template
meta_description: Template for breast cancer mammogram classification with Label Studio
community: true
community_author: redeipirati
community_contributors: carly-bartel
community_repo: awesome-label-studio-config
github_repo: humanSignal/awesome-label-studio-config
repo_url: https://github.com/HumanSignal/awesome-label-studio-config/tree/main/label-configs/breast-cancer-mammogram-classification
---


<img src="/images/templates/breast-cancer-mammogram-classification.gif" alt="" class="gif-border" width="552px" height="408px" />

This labeling config provides a comprehensive interface for breast cancer mammogram analysis using the BI-RADS classification system. It enables radiologists to classify mammograms, assess breast density, and document findings for both breasts.

## Labeling Configuration

```html
<View>
  <!-- Header for context -->
  <Header value="Breast Cancer Mammogram Classification" />

  <!-- Instructions -->
  <View style="margin-bottom: 20px;">
    <Header value="Please review the standard mammographic views (CC and MLO) of both breasts. Compare corresponding views (e.g., L-CC with R-CC). Label each breast individually, and report any findings." />
    <Text name="birads_legend" value="BI-RADS: 0 = Incomplete, 1 = Negative, 2 = Benign, 3 = Probably Benign, 4 = Suspicious, 5 = Highly Suggestive of Malignancy, 6 = Known Cancer" />
  </View>

  <!-- CC Views -->
  <View style="margin-bottom: 10px; display: flex; gap: 20px; justify-content: center;">
    <View style="text-align: center; width: 450px; height: 450px;">
      <Header value="Left CC" />
      <Image name="left_cc" value="$img1" style="width:100%; height:100%; object-fit: contain;" />
    </View>
    <View style="text-align: center; width: 450px; height: 450px;">
      <Header value="Right CC" />
      <Image name="right_cc" value="$img3" style="width:100%; height:100%; object-fit: contain;" />
    </View>
  </View>

  <!-- MLO Views -->
  <View style="margin-bottom: 20px; display: flex; gap: 20px; justify-content: center;">
    <View style="text-align: center; width: 450px; height: 450px;">
      <Header value="Left MLO" />
      <Image name="left_mlo" value="$img2" style="width:100%; height:100%; object-fit: contain;" />
    </View>
    <View style="text-align: center; width: 450px; height: 450px;">
      <Header value="Right MLO" />
      <Image name="right_mlo" value="$img4" style="width:100%; height:100%; object-fit: contain;" />
    </View>
  </View>

  <!-- Left Breast -->
  <View style="margin-top: 20px;">
    <Header value="Left Breast: BI-RADS Classification" />
    <Choices name="birads_left" toName="left_cc,right_cc,left_mlo,right_mlo" choice="single" required="true">
      <Choice value="0 - Incomplete" />
      <Choice value="1 - Negative" />
      <Choice value="2 - Benign" />
      <Choice value="3 - Probably Benign" />
      <Choice value="4 - Suspicious Abnormality" />
      <Choice value="5 - Highly Suggestive of Malignancy" />
      <Choice value="6 - Known Biopsy-Proven Malignancy" />
    </Choices>

    <Header value="Left Breast: Density" />
    <Choices name="density_left" toName="left_cc,right_cc,left_mlo,right_mlo" choice="single">
      <Choice value="A - Almost entirely fatty" />
      <Choice value="B - Scattered fibroglandular densities" />
      <Choice value="C - Heterogeneously dense" />
      <Choice value="D - Extremely dense" />
    </Choices>

    <Header value="Left Breast: Findings (Optional)" />
    <Choices name="findings_left" toName="left_cc,right_cc,left_mlo,right_mlo" choice="multiple">
      <Choice value="Mass" />
      <Choice value="Calcifications" />
      <Choice value="Architectural Distortion" />
      <Choice value="Asymmetry" />
      <Choice value="Skin/Nipple Retraction" />
    </Choices>
  </View>

  <!-- Right Breast -->
  <View style="margin-top: 30px;">
    <Header value="Right Breast: BI-RADS Classification" />
    <Choices name="birads_right" toName="left_cc,right_cc,left_mlo,right_mlo" choice="single" required="true">
      <Choice value="0 - Incomplete" />
      <Choice value="1 - Negative" />
      <Choice value="2 - Benign" />
      <Choice value="3 - Probably Benign" />
      <Choice value="4 - Suspicious Abnormality" />
      <Choice value="5 - Highly Suggestive of Malignancy" />
      <Choice value="6 - Known Biopsy-Proven Malignancy" />
    </Choices>

    <Header value="Right Breast: Density" />
    <Choices name="density_right" toName="left_cc,right_cc,left_mlo,right_mlo" choice="single">
      <Choice value="A - Almost entirely fatty" />
      <Choice value="B - Scattered fibroglandular densities" />
      <Choice value="C - Heterogeneously dense" />
      <Choice value="D - Extremely dense" />
    </Choices>

    <Header value="Right Breast: Findings (Optional)" />
    <Choices name="findings_right" toName="left_cc,right_cc,left_mlo,right_mlo" choice="multiple">
      <Choice value="Mass" />
      <Choice value="Calcifications" />
      <Choice value="Architectural Distortion" />
      <Choice value="Asymmetry" />
      <Choice value="Skin/Nipple Retraction" />
    </Choices>
  </View>

  <!-- Free Text Observation -->
  <View style="margin-top: 30px;">
    <Header value="Additional Observations / Notes (Optional)" />
    <TextArea
      name="notes"
      toName="left_cc,right_cc,left_mlo,right_mlo"
      rows="5"
      placeholder="Describe any notable findings, technical issues, or comparison to prior exams."
    />
  </View>
</View>
```

## About the labeling configuration

All labeling configurations must be wrapped in [View](/tags/view.html) tags.

This configuration uses the following tags:

- [Image](/tags/image.html)
- [Choices](/tags/choices.html)
- [TextArea](/tags/textarea.html)
- [View](/tags/view.html)
- [Header](/tags/header.html)

## Usage Instructions

- **Image Display**: This config displays four mammogram views (Left CC, Left MLO, Right CC, Right MLO) in a grid layout.
- **BI-RADS Classification**: Each breast can be classified using the standard BI-RADS categories (0-6).
- **Density Assessment**: Breast density can be classified using the A-D scale.
- **Findings Documentation**: Multiple choice options for common findings (Mass, Calcifications, etc.).
- **Notes**: Free text area for additional observations and technical notes.

