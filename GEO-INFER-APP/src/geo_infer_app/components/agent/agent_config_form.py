"""
Agent Configuration Form Component

A React component for configuring geospatial agents with UI forms
generated from agent configuration schemas.
"""

import React from "react"
import PropTypes from "prop-types"
import { useForm, Controller } from "react-hook-form"
import { 
    Box, Button, FormControl, FormLabel, FormHelperText, 
    Input, Select, Checkbox, Textarea, NumberInput,
    NumberInputField, NumberInputStepper, NumberIncrementStepper,
    NumberDecrementStepper, Stack, Heading, Divider,
    Accordion, AccordionItem, AccordionButton, AccordionPanel,
    AccordionIcon, Alert, AlertIcon
} from "@chakra-ui/react"

const AgentConfigForm = ({ 
    schema, 
    initialValues = {}, 
    onSubmit, 
    onCancel,
    isLoading = false,
    error = null
}) => {
    const { handleSubmit, control, formState: { errors } } = useForm({
        defaultValues: initialValues
    });

    // Group fields by their group property
    const fieldsByGroup = {};
    schema.fields.forEach(field => {
        const groupName = field.group || "Basic";
        if (!fieldsByGroup[groupName]) {
            fieldsByGroup[groupName] = [];
        }
        fieldsByGroup[groupName].push(field);
    });

    // Sort groups by their order
    const sortedGroups = Object.entries(fieldsByGroup).sort((a, b) => {
        const groupA = schema.groups.find(g => g.name === a[0]) || { order: 999 };
        const groupB = schema.groups.find(g => g.name === b[0]) || { order: 999 };
        return groupA.order - groupB.order;
    });

    // Render a field based on its type
    const renderField = (field) => {
        const isRequired = field.required;
        const fieldError = errors[field.name];

        // Check field dependencies
        const shouldRender = !field.dependencies || field.dependencies.every(dep => {
            return !!initialValues[dep];
        });

        if (!shouldRender) {
            return null;
        }

        return (
            <FormControl 
                key={field.name} 
                isRequired={isRequired} 
                isInvalid={!!fieldError}
                mb={4}
            >
                <FormLabel>{field.label}</FormLabel>
                <Controller
                    name={field.name}
                    control={control}
                    rules={{ 
                        required: isRequired ? `${field.label} is required` : false,
                        ...(field.validation?.min !== undefined ? { min: field.validation.min } : {}),
                        ...(field.validation?.max !== undefined ? { max: field.validation.max } : {}),
                        ...(field.validation?.pattern ? { pattern: field.validation.pattern } : {})
                    }}
                    render={({ field: formField }) => {
                        switch (field.field_type) {
                            case "string":
                                return <Input {...formField} />;
                            case "number":
                                return (
                                    <NumberInput 
                                        {...formField} 
                                        min={field.validation?.min}
                                        max={field.validation?.max}
                                        step={0.1}
                                    >
                                        <NumberInputField />
                                        <NumberInputStepper>
                                            <NumberIncrementStepper />
                                            <NumberDecrementStepper />
                                        </NumberInputStepper>
                                    </NumberInput>
                                );
                            case "boolean":
                                return <Checkbox {...formField} isChecked={formField.value} />;
                            case "object":
                                return <Textarea {...formField} value={JSON.stringify(formField.value, null, 2)} />;
                            case "array":
                                return <Textarea {...formField} value={JSON.stringify(formField.value, null, 2)} />;
                            case "select":
                                return (
                                    <Select {...formField}>
                                        {field.options.map(option => (
                                            <option key={option.value} value={option.value}>
                                                {option.label}
                                            </option>
                                        ))}
                                    </Select>
                                );
                            case "multiselect":
                                // This is a simplified implementation
                                return (
                                    <Select {...formField} multiple>
                                        {field.options.map(option => (
                                            <option key={option.value} value={option.value}>
                                                {option.label}
                                            </option>
                                        ))}
                                    </Select>
                                );
                            case "geolocation":
                                // Simplified geolocation input
                                return (
                                    <Stack direction="row" spacing={2}>
                                        <NumberInput placeholder="Latitude">
                                            <NumberInputField />
                                        </NumberInput>
                                        <NumberInput placeholder="Longitude">
                                            <NumberInputField />
                                        </NumberInput>
                                    </Stack>
                                );
                            default:
                                return <Input {...formField} />;
                        }
                    }}
                />
                {field.description && !fieldError && (
                    <FormHelperText>{field.description}</FormHelperText>
                )}
                {fieldError && (
                    <FormHelperText color="red.500">{fieldError.message}</FormHelperText>
                )}
            </FormControl>
        );
    };

    return (
        <Box as="form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <Heading size="md" mb={4}>{schema.title}</Heading>
            {error && (
                <Alert status="error" mb={4}>
                    <AlertIcon />
                    {error}
                </Alert>
            )}
            
            <Accordion defaultIndex={[0]} allowMultiple>
                {sortedGroups.map(([groupName, fields]) => {
                    const group = schema.groups.find(g => g.name === groupName) || {
                        label: groupName,
                        name: groupName
                    };
                    
                    return (
                        <AccordionItem key={groupName}>
                            <h2>
                                <AccordionButton>
                                    <Box flex="1" textAlign="left" fontWeight="medium">
                                        {group.label}
                                    </Box>
                                    <AccordionIcon />
                                </AccordionButton>
                            </h2>
                            <AccordionPanel pb={4}>
                                {fields.sort((a, b) => a.order - b.order).map(renderField)}
                            </AccordionPanel>
                        </AccordionItem>
                    );
                })}
            </Accordion>
            
            <Divider my={6} />
            
            <Stack direction="row" spacing={4} justifyContent="flex-end">
                {onCancel && (
                    <Button onClick={onCancel} variant="outline">
                        Cancel
                    </Button>
                )}
                <Button 
                    type="submit" 
                    colorScheme="blue" 
                    isLoading={isLoading}
                >
                    Save Configuration
                </Button>
            </Stack>
        </Box>
    );
};

AgentConfigForm.propTypes = {
    schema: PropTypes.shape({
        title: PropTypes.string.isRequired,
        description: PropTypes.string,
        fields: PropTypes.arrayOf(PropTypes.shape({
            name: PropTypes.string.isRequired,
            field_type: PropTypes.string.isRequired,
            label: PropTypes.string.isRequired,
            description: PropTypes.string,
            required: PropTypes.bool,
            options: PropTypes.arrayOf(PropTypes.shape({
                label: PropTypes.string.isRequired,
                value: PropTypes.any.isRequired
            })),
            validation: PropTypes.object,
            dependencies: PropTypes.arrayOf(PropTypes.string),
            group: PropTypes.string,
            order: PropTypes.number
        })).isRequired,
        groups: PropTypes.arrayOf(PropTypes.shape({
            name: PropTypes.string.isRequired,
            label: PropTypes.string.isRequired,
            order: PropTypes.number
        }))
    }).isRequired,
    initialValues: PropTypes.object,
    onSubmit: PropTypes.func.isRequired,
    onCancel: PropTypes.func,
    isLoading: PropTypes.bool,
    error: PropTypes.string
};

export default AgentConfigForm; 