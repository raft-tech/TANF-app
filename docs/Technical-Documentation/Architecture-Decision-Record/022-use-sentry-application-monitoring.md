# 1. Record architecture decisions

Date: 2024-10-06

## Status

Pending approval

## Context

Application health and error monitoring help to identify and resolve issues in production. It provides visibility to errors and the underlying issues within the software and help to make impactful decisions to resolve such issues.

While with logs (logs in cloud.gov or PLG) -if available- it is possible to track timeline of events, logs are not enough for debugging unhandled exception since the stack trace related to exception might be lost.

Moreover, our response is reactive, meaning we only address problems after they occur, such as system crashes and unhandled exceptions. This results in delayed issue resolution and makes it difficult to proactively identify root causes. 

## Decision

### Why Sentry

#### 1. Error Tracking and Performance Monitoring

Sentry captures unhandled exceptions and incorporates detail context about exceptions including error messages, stack traces, affected URLs and user data information. Such information is essential in demystifying the cause of error.

Additionally, as can be seen in the image below, the following information is available:

- Frequency: shows the frequency detail of error 
- Timeline: when has the error happened in a period
- Can create a ticket and assign automatically
- Variables at each step of stack trace. This is very important for debugging

<p style="text-align:center; margin:0; padding:0;">Issues with filter enabled</p>

![Issues with filter enabled](../images/sentry/1.%20Issues%20with%20filter%20enabled.png)

<p style="text-align:center; margin:0;padding:0;">Detail exceptions</p>

![Detail exceptions](../images/sentry/3.%20detail%20about%20exception.png)

<p style="text-align:center; margin:0; padding:0;">Full stack trace of the exceptions</p>

![Full stack trace of the exceptions](../images/sentry/4.%20full%20stack%20trace%20of%20the%20exceptions.png)


Performance monitoring in Sentry can greatly enhance backend application by providing real-time insights into how TANF app is performing. It tracks various metrics such as response time, database queries, and external API calls, with which we can identify performance bottlenecks to our backend app.

A unique ability of Sentry is that it can link performance issues and group them together. This gives us the ability to attack and resolve more critical issues with highest impact first. Not only it can detect issues with web transactions, it also detects problems with DB queries as well as function regressions (if the duration of function has increased)

We will use Architecture Decision Records, as described by Michael Nygard in this article: http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions

## Consequences

The benefits and any known/potential risks of the decision should be described herein. See Michael Nygard's article, linked above, for more details.

## Notes

Briefly describe any additional information relevant to the decision here, such as issues created to track implementation. 
