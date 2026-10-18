---
doc_id: OP-04
doc_type: operating_procedure
robot_model: all
firmware: all
last_updated: 2025-07-01
---

# Operating Procedure: Maintenance Notification and Spare-Part Stock in the ERP

## Purpose

How to check whether a spare part is in stock, and how to report a fault to maintenance through the ERP. This procedure applies to all models.

## Finding the part

1. Look up the fix in the troubleshooting guide for the error code. The guides list the part number for each model, for example SP-1001 for the AMR-100 wheel motor assembly.
2. Make sure the part matches the robot model. Many parts exist in one version for the AMR-100 and one for the AMR-200, and they are not interchangeable.

## Checking stock

1. In the ERP, open **Spare parts** and search by part number or description.
2. Filter by compatible model.
3. Note the stock, the storage location and the lead time in days.
4. If the stock is 0, the part has to be ordered. The lead time tells you how long the robot will be out of service.

## Creating the maintenance notification

1. In the ERP, open **Maintenance notifications** and create a new notification.
2. Fill in the robot id, a short title with the error code and symptom (for example "E42 wheel stall on robot 2"), and a description with the telemetry you saw, the fix from the guide, the part number and the stock you found.
3. Choose the priority:
   - **high**: the robot is out of service, or a needed part is out of stock.
   - **medium**: the robot works, but with reduced performance.
   - **low**: planned work that can wait for the next maintenance window.
4. Save. Every new notification is saved as a **draft**.

## Approval

1. A draft notification does nothing until a maintenance supervisor approves it in the ERP.
2. Only a person can approve a notification. Automated tools and assistants may prepare drafts, but they never approve them.
3. A notification can be approved only once. If it was already approved, the ERP shows an error.

## Tips

- Create the notification on the same day as the fault, even if the part is out of stock. Late notifications were a main cause of long downtime in past incidents.
