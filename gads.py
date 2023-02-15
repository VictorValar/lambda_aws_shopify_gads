def main(
    client,
    customer_id,
    conversion_action_id,
    gclid,
    conversion_date_time,
    conversion_value,
    conversion_custom_variable_id,
    conversion_custom_variable_value,
    gbraid,
    wbraid,
):
    """Creates a click conversion with a default currency of USD.

    Args:
        client: An initialized GoogleAdsClient instance.
        customer_id: The client customer ID string.
        conversion_action_id: The ID of the conversion action to upload to.
        gclid: The Google Click Identifier ID. If set, the wbraid and gbraid
            parameters must be None.
        conversion_date_time: The the date and time of the conversion (should be
            after the click time). The format is 'yyyy-mm-dd hh:mm:ss+|-hh:mm',
            e.g. '2021-01-01 12:32:45-08:00'.
        conversion_value: The conversion value in the desired currency.
        conversion_custom_variable_id: The ID of the conversion custom
            variable to associate with the upload.
        conversion_custom_variable_value: The str value of the conversion custom
            variable to associate with the upload.
        gbraid: The GBRAID for the iOS app conversion. If set, the gclid and
            wbraid parameters must be None.
        wbraid: The WBRAID for the iOS app conversion. If set, the gclid and
            gbraid parameters must be None.
    """
    click_conversion = client.get_type("ClickConversion")
    conversion_upload_service = client.get_service("ConversionUploadService")
    conversion_action_service = client.get_service("ConversionActionService")
    click_conversion.conversion_action = conversion_action_service.conversion_action_path(
        customer_id, conversion_action_id
    )

    # Sets the single specified ID field.
    if gclid:
        click_conversion.gclid = gclid
    elif gbraid:
        click_conversion.gbraid = gbraid
    else:
        click_conversion.wbraid = wbraid

    click_conversion.conversion_value = float(conversion_value)
    click_conversion.conversion_date_time = conversion_date_time
    click_conversion.currency_code = "USD"

    if conversion_custom_variable_id and conversion_custom_variable_value:
        conversion_custom_variable = client.get_type("CustomVariable")
        conversion_custom_variable.conversion_custom_variable = conversion_upload_service.conversion_custom_variable_path(
            customer_id, conversion_custom_variable_id
        )
        conversion_custom_variable.value = conversion_custom_variable_value
        click_conversion.custom_variables.append(conversion_custom_variable)

    request = client.get_type("UploadClickConversionsRequest")
    request.customer_id = customer_id
    request.conversions.append(click_conversion)
    request.partial_failure = True
    conversion_upload_response = conversion_upload_service.upload_click_conversions(
        request=request,
    )
    uploaded_click_conversion = conversion_upload_response.results[0]
    print(
        f"Uploaded conversion that occurred at "
        f'"{uploaded_click_conversion.conversion_date_time}" from '
        f'Google Click ID "{uploaded_click_conversion.gclid}" '
        f'to "{uploaded_click_conversion.conversion_action}"'
    )
