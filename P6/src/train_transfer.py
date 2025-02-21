from models.transfered_model import TransferedModel
from models.random_model import RandomModel
from config import image_size
import matplotlib.pyplot as plt
from tensorflow.keras.utils import image_dataset_from_directory
import tensorflow as tf


# Your code should change these values based on your choice of dataset for the transfer task
# -------------
input_shape = (image_size[0], image_size[1], 3)
categories_count = 2
# -------------

models = {
    'random_model': RandomModel,
    'transfered_model': TransferedModel,
}

def get_transfer_datasets():
    train_ds = image_dataset_from_directory(
        'transfer_train',
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=image_size,
        label_mode='categorical',
        batch_size=32
    )

    val_ds = image_dataset_from_directory(
        'transfer_train',
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=image_size,
        label_mode='categorical',
        batch_size=32
    )

    test_ds = image_dataset_from_directory(
        'transfer_test',
        seed=123,
        image_size=image_size,
        label_mode='categorical',
        batch_size=32
    )

    # Enable caching and prefetching for better performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, test_ds

def plot_history_diff(initial_hist, transfered_hist):
    val_acc_initial = initial_hist.history['val_accuracy']
    val_acc_tranfered = transfered_hist.history['val_accuracy']

    epochs = range(1, len(val_acc_initial) + 1)
    
    plt.figure(figsize=(12, 6))
    plt.plot(epochs, val_acc_initial, 'b', label='Without Transfer Learning')
    plt.plot(epochs, val_acc_tranfered, 'r', label='With Transfer Learning')
    plt.grid(True)
    plt.legend()
    plt.title('Far Transfer from Facial Recognition to Dogs vs Cats Classification')
    plt.xlabel('Epoch')
    plt.ylabel('Validation Accuracy')
    plt.savefig('transfer_learning_comparison.png')
    plt.show()

if __name__ == "__main__":
    # Your code should change the number of epochs
    epochs = 10
    print('* Data preprocessing')
    train_dataset, validation_dataset, test_dataset = get_transfer_datasets()
    histories = []
    
    print("\nChecking dataset contents:")
    print(f"Number of training batches: {len(list(train_dataset))}")
    print(f"Number of validation batches: {len(list(validation_dataset))}")
    print(f"Number of test batches: {len(list(test_dataset))}")
    
    for name, model_class in models.items():
        print(f'\n* Training {name} for {epochs} epochs')
        model = model_class(input_shape, categories_count)
        model.print_summary()
        history = model.train_model(train_dataset, validation_dataset, epochs)
        histories.append(history)
        print(f'* Evaluating {name}')
        model.evaluate(test_dataset)
        print(f'* Confusion Matrix for {name}')
        print(model.get_confusion_matrix(test_dataset))
    
    assert len(histories) == 2, "The number of trained models is not equal to two"
    plot_history_diff(*histories)
