# MMIF and PBCore

Some notes on the mappings of elements from the MMIF file in the "everything and the kitched sink" example to PBCore (see [index.md](index) and [raw.json](raw.json)).

The relevant information that we have in MMIF is in the following types:

1. Instances of *TimeFrame* with frameType "bars-and-tone" or "slate". These directly refer back to time slices in the video.
2. Instances of *SemanticTag* with tagName "Date", "Title", "Host" or "Producer". These can be traced back to the part of the video where the information was obtained (that is, the location of the slate), but this is not needed here because it is not required by PBCore (or even allowed in the PBCore elements that we would be using).
3. Instances of *NamedEntity* with category "Person", "Location" or "Organization". These do need to be traced back because we want to index on the locations in the video where a subject occurs.

Tracing back to the source location requires some processing because while the information is available in the MMIF file it is not explicitly stated in the *NamedEntity* annotation.

A note on collaboration on this. The CLAMS team could do one of the following:

1. Provide code and an API that makes it easy to get the information from a MMIF file that is needed.
2. Create code that extracts the needed in formation from a MMIF file and outputs it in some kind of generic format.
3. Create code that extracts the information and creates PBCore output.

Most of the work is in item 1 and that would be the minimal thing to do for CLAMS, but this document assumes for now that the CLAMS team also creates PBCore output.

### Mappings from MMIF to PBCore

The PBCore to be created has a top-level *pbcoreDescriptionDocument* element:

```xml
<pbcoreDescriptionDocument xmlns="http://www.pbcore.org/PBCore/PBCoreNamespace.html">
</pbcoreDescriptionDocument>
```

Within this top-level element we may add the following sub elements: *pbcoreAssetDate*, *pbcoreTitle*, *pbcoreContributor*, *pbcoreSubject*, *pbcoreAnnotation* and *pbcoreDescription*. The examples below for the MMIF example file [raw.json](raw.json) are based on the descriptions in [http://pbcore.org/elements](http://pbcore.org/elements) and feedback from Kevin.

To map the MMIF <u>time frames</u> we need a need an element that allows us to express the type and the start and end times. The only one I can see that is not obviously intended for other uses is *pbcoreDescription* (in an earlier version of this document I used *pbcorePart* which is really not appropriate).

```xml
<pbcoreDescription descriptionType="bars-and-tone" startTime="0" endTime="2600" />
<pbcoreDescription descriptionType="slate" startTime="2700" endTime="5300" />
```

Instead of *descriptionType* it may be more appropriate to use *segmentType*, but from the descriptions given in [http://pbcore.org/elements/pbcoredescription](http://pbcore.org/elements/pbcoredescription) it is not really clear to me which one is best. Another question I have is whether the attribute values for start and end can be milliseconds from the beginning of the video.

It was suggested that as an alternative we could use *instantiationTimeStart*, which can be repetaed:

```xml
<instantiationTimeStart annotation="bars-and-tone-start">0</instantiationTimeStart>
<instantiationTimeStart annotation="bars-and-tone-end">2600</instantiationTimeStart>
<instantiationTimeStart annotation="slate-start">2700</instantiationTimeStart>
<instantiationTimeStart annotation="slate-end">5300</instantiationTimeStart>
```

This looks rather forced to me and would also require using a *pbcoreInstantiationDocument* toplevel tag I think, so I will for now dismiss this summarily.

The <u>semantic tags</u> in MMIF have direct and unproblematic mappings to PBCore elements:

Date → pbcoreAssetDate
Title  → pbcoreTitle
Host → pbcoreContributor
Producer → pbcoreContributor

```xml
<pbcoreAssetDate dateType="broadcast">1982-05-12</pbcoreAssetDate>
```

```xml
<pbcoreTitle>Loud Dogs</pbcoreTitle>
```

```xml
<pbcoreContributor>
   <contributor>Jim Lehrer</contributor>
   <contributorRole>Host</contributorRole>
</pbcoreContributor>
```

```xml
<pbcoreContributor>
   <contributor>Sara Just</contributor>
   <contributorRole>Producer</contributorRole>
</pbcoreContributor>
```

For the <u>named entities</u> we can use *pbcoreSubject*:

```xml
<pbcoreSubject subjectType="Person" ref="SOME_REF"
               startTime="7255" endTime="8425">Jim Lehrer</pbcoreSubject>
```

```xml
<pbcoreSubject subjectType="Organization" ref="SOME_REF"
               startTime="10999" endTime="11350">PBS</pbcoreSubject>
```

```xml
<pbcoreSubject subjectType="Location" ref="SOME_REF"
               startTime="21000" endTime="21000">New York</pbcoreSubject>
```

I am not sure how to spin the attributes so this here is my best guesstimate. Note that "Jim Lehrer" shows up both as a contributor and as a subject, the former because he was mentioned in the slate and the latter because his name was used in the transcript.

The subject type is  the entity category for all of these and the *ref* property is used to refer to some external authoritative source.

Start and end time are in milliseconds. For the first two they are generated by finding the tokens in the transcript text documents (by comparing start and end character offsets) and then tracking those to the time frames that they are aligned with.

For the third, we know the named entity occurs in some text document (created by Tesseract) and we track that document to the bounding box generated by EAST that the document is aligned with. That bounding box has a *timePoint* attribute that is used for both start and end time. Note that if there had be a second text box for the "Dog in New York" text (that is, if the time the image was displayed on screen was a little bit longer) then that box would have its own time point and the end time for "New York" would have been 22000.

It is possible that there may be many instantiations of *pbcoreSubject*, for example for a common entity like Boston. There is some unease on having multiple elements for a single named entity, but it is not clear what to do about it (use other element? only have one instance?). For now, we will dump all entities in PBCore subject elements and see how that pans out. In general, it seems fairly easy to export relevant information from MMIF into PBCore without loss of information, and what is exported and what the exact landing spots are going to be can be driven by PBCore-specific reasons.

Finally, here is all the above in one XML file, adding some identifier that we get from the input:

```xml
<pbcoreDescriptionDocument xmlns="http://www.pbcore.org/PBCore/PBCoreNamespace.html">

  <pbcoreAssetDate dateType="broadcast">1982-05-12</pbcoreAssetDate>

  <pbcoreIdentifier source="http://americanarchiveinventory.org">SOME_ID</pbcoreIdentifier>

  <pbcoreTitle>Loud Dogs</pbcoreTitle>

  <pbcoreSubject subjectType="Person" ref="SOME_REF"
                 startTime="7255" endTime="8425">Jim Lehrer</pbcoreSubject>

  <pbcoreSubject subjectType="Organization" ref="SOME_REF"
                 startTime="10999" endTime="11350">PBS</pbcoreSubject>

  <pbcoreSubject subjectType="Location" ref="SOME_REF"
                 startTime="21000" endTime="21000">New York</pbcoreSubject>

  <pbcoreDescription descriptionType="bars-and-tone" startTime="0" endTime="2600" />

  <pbcoreDescription descriptionType="slate" startTime="2700" endTime="5300" />

  <pbcoreContributor>
    <contributor>Jim Lehrer</contributor>
    <contributorRole>Host</contributorRole>
  </pbcoreContributor>

  <pbcoreContributor>
    <contributor>Sara Just</contributor>
    <contributorRole>Producer</contributorRole>
  </pbcoreContributor>

</pbcoreDescriptionDocument>
```

