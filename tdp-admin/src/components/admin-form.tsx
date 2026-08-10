"use client";

import { useState } from "react";
import {
  Alert,
  Button,
  ErrorMessage,
  FormGroup,
  Label,
  Select,
  TextInput,
  Textarea,
} from "@trussworks/react-uswds";
import {
  useForm,
  type FieldError,
  type RegisterOptions,
} from "react-hook-form";
import {
  getClientValidationRules,
  getDefaultAdminFormValues,
  type AdminFormField,
  type AdminFormMetadata,
  type AdminFormValues,
  type NormalizedAdminFormErrors,
} from "@/lib/admin-form";

type AdminFormProps = {
  metadata: AdminFormMetadata;
  csrfToken: string | null;
  cancelHref?: string;
  cancelLabel?: string;
};

type AdminFormMutationResponse = {
  ok?: boolean;
  errors?: NormalizedAdminFormErrors;
  metadata?: AdminFormMetadata;
};

function fieldId(field: AdminFormField) {
  return `admin-field-${field.name}`;
}

function describedBy(field: AdminFormField, hasError: boolean) {
  const ids = [];

  if (field.help_text) {
    ids.push(`${fieldId(field)}-hint`);
  }

  if (hasError) {
    ids.push(`${fieldId(field)}-error`);
  }

  return ids.length ? ids.join(" ") : undefined;
}

function fieldErrorMessage(error?: FieldError) {
  return typeof error?.message === "string" ? error.message : "";
}

export function AdminForm({
  metadata,
  csrfToken,
  cancelHref,
  cancelLabel = "Back",
}: AdminFormProps) {
  const [formMetadata, setFormMetadata] = useState(metadata);
  const [serverErrors, setServerErrors] = useState<string[]>([]);
  const [statusMessage, setStatusMessage] = useState("");
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<AdminFormValues>({
    defaultValues: getDefaultAdminFormValues(metadata),
    mode: "onBlur",
    reValidateMode: "onChange",
  });

  function applyServerErrors(normalizedErrors?: NormalizedAdminFormErrors) {
    setServerErrors(normalizedErrors?.non_field_errors ?? []);

    for (const [name, messages] of Object.entries(
      normalizedErrors?.field_errors ?? {}
    )) {
      setError(name, {
        type: "server",
        message: messages.join(" "),
      });
    }
  }

  async function submit(values: AdminFormValues) {
    setServerErrors([]);
    setStatusMessage("");

    if (!csrfToken) {
      setServerErrors(["A CSRF token is required before saving this form."]);
      return;
    }

    const response = await fetch(`/api/admin${formMetadata.submit_url}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(values),
    });
    const data = (await response
      .json()
      .catch(() => ({}))) as AdminFormMutationResponse;

    if (!response.ok || data.ok === false) {
      if (data.errors) {
        applyServerErrors(data.errors);
      } else {
        setServerErrors([`Save failed with status ${response.status}.`]);
      }
      return;
    }

    if (data.metadata) {
      setFormMetadata(data.metadata);
      reset(getDefaultAdminFormValues(data.metadata));
    }

    setStatusMessage("Saved.");
  }

  return (
    <form className="admin-form" onSubmit={handleSubmit(submit)} noValidate>
      {statusMessage && (
        <Alert
          type="success"
          heading="Saved"
          headingLevel="h2"
          className="admin-form__alert"
        >
          {statusMessage}
        </Alert>
      )}

      {serverErrors.length > 0 && (
        <Alert
          type="error"
          heading="Could not save form"
          headingLevel="h2"
          className="admin-form__alert"
          validation
        >
          <ul>
            {serverErrors.map((message) => (
              <li key={message}>{message}</li>
            ))}
          </ul>
        </Alert>
      )}

      <div className="admin-form__fields">
        {formMetadata.fields.map((field) => {
          const error = errors[field.name];
          const message = fieldErrorMessage(error as FieldError | undefined);
          const hasError = Boolean(message);
          const registration = register(
            field.name,
            getClientValidationRules(field) as RegisterOptions<AdminFormValues>
          );
          const textInputType =
            field.type === "number" || field.type === "email"
              ? field.type
              : "text";

          return (
            <FormGroup key={field.name} error={hasError}>
              {field.type !== "checkbox" && (
                <Label
                  htmlFor={fieldId(field)}
                  error={hasError}
                  requiredMarker={field.required}
                >
                  {field.label}
                </Label>
              )}
              {field.help_text && (
                <div className="usa-hint" id={`${fieldId(field)}-hint`}>
                  {field.help_text}
                </div>
              )}
              {hasError && (
                <ErrorMessage id={`${fieldId(field)}-error`}>
                  {message}
                </ErrorMessage>
              )}

              {field.type === "select" && (
                <Select
                  id={fieldId(field)}
                  name={registration.name}
                  inputRef={registration.ref}
                  onBlur={registration.onBlur}
                  onChange={registration.onChange}
                  validationStatus={hasError ? "error" : undefined}
                  aria-describedby={describedBy(field, hasError)}
                >
                  {field.choices.map((choice) => (
                    <option
                      key={`${field.name}-${choice.value}`}
                      value={choice.value}
                    >
                      {choice.label}
                    </option>
                  ))}
                </Select>
              )}

              {field.type === "multiselect" && (
                <Select
                  id={fieldId(field)}
                  name={registration.name}
                  inputRef={registration.ref}
                  onBlur={registration.onBlur}
                  onChange={registration.onChange}
                  validationStatus={hasError ? "error" : undefined}
                  aria-describedby={describedBy(field, hasError)}
                  multiple
                  size={Math.min(Math.max(field.choices.length, 3), 8)}
                >
                  {field.choices
                    .filter((choice) => choice.value !== "")
                    .map((choice) => (
                      <option
                        key={`${field.name}-${choice.value}`}
                        value={choice.value}
                      >
                        {choice.label}
                      </option>
                    ))}
                </Select>
              )}

              {field.type === "checkbox" && (
                <div className="usa-checkbox">
                  <input
                    className="usa-checkbox__input"
                    id={fieldId(field)}
                    type="checkbox"
                    aria-describedby={describedBy(field, hasError)}
                    {...registration}
                  />
                  <label className="usa-checkbox__label" htmlFor={fieldId(field)}>
                    {field.label}
                    {field.required && (
                      <abbr
                        title="required"
                        className="usa-hint usa-hint--required"
                      >
                        *
                      </abbr>
                    )}
                  </label>
                </div>
              )}

              {field.type === "textarea" && (
                <Textarea
                  id={fieldId(field)}
                  name={registration.name}
                  inputRef={registration.ref}
                  onBlur={registration.onBlur}
                  onChange={registration.onChange}
                  error={hasError}
                  aria-describedby={describedBy(field, hasError)}
                />
              )}

              {field.type !== "select" &&
                field.type !== "multiselect" &&
                field.type !== "checkbox" &&
                field.type !== "textarea" && (
                  <TextInput
                    id={fieldId(field)}
                    type={textInputType}
                    validationStatus={hasError ? "error" : undefined}
                    aria-describedby={describedBy(field, hasError)}
                    {...registration}
                  />
                )}
            </FormGroup>
          );
        })}
      </div>

      <div className="admin-form__actions">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : "Save"}
        </Button>
        {cancelHref && (
          <a className="usa-button usa-button--outline" href={cancelHref}>
            {cancelLabel}
          </a>
        )}
      </div>
    </form>
  );
}
